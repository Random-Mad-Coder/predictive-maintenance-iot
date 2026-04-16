# Predictive Maintenance IoT Pipeline

End-to-end IoT system for monitoring a DC motor's health using an Arduino Uno and AWS. Sensor data flows from hardware through a cloud pipeline into a live dashboard with configurable alerting.

Built as a portfolio project for Cloud / Data Engineering roles.

## Architecture

![Architecture diagram](docs/architecture.svg)

**Data ingestion:** An Arduino Uno reads temperature from an NTC thermistor attached to a DC motor. A Python bridge script adds a UTC timestamp and publishes the payload to AWS IoT Core via MQTT (TLS, QoS 1). Two IoT Rules route every message to a writer Lambda (stores to DynamoDB) and an alerter Lambda (checks against a configurable threshold and sends email alerts via SNS).

**Data serving:** A static dashboard hosted on S3 behind CloudFront (HTTPS) polls an HTTP API Gateway. Two Lambda functions handle reads - one for metric queries, one for threshold configuration (read + write). CORS is handled entirely by the Lambdas.

## Tech stack

| Layer | Technology |
|---|---|
| Sensor | Arduino Uno, NTC thermistor (Steinhart-Hart), HG7881 motor driver |
| Bridge | Python, pyserial, paho-mqtt |
| Messaging | AWS IoT Core (MQTT, TLS, X.509 certificates) |
| Compute | AWS Lambda (Python 3.12, boto3) |
| Storage | Amazon DynamoDB (single-table, partition key + sort key) |
| API | Amazon API Gateway (HTTP API) |
| Alerting | Amazon SNS (email) |
| Frontend | HTML / CSS / JavaScript, Chart.js |
| Hosting | Amazon S3, Amazon CloudFront (HTTPS, OAC) |

## Features

- **Live temperature chart** Chart.js time series with configurable sliding window (10 min / 30 min / 1 hour)
- **Dynamic threshold** adjustable via the dashboard UI, persisted in DynamoDB, used by the alerter Lambda
- **Email alerts** SNS notification when temperature exceeds threshold
- **Metric cards** current temperature, min/max, data point count, Arduino uptime
- **Pause / resume** toggle live polling without losing existing data
- **Y-axis scaling** always shows both current data and threshold line

## DynamoDB design

Single table `motor-metrics` with a composite key:

| Key | Type | Purpose |
|---|---|---|
| `motor_id` (partition) | String | Groups data by motor (e.g. `N20`) |
| `timestamp` (sort) | String (ISO 8601) | Orders measurements chronologically |

Configuration entries use `timestamp = "CONFIG"` as a sentinel value, storing fields like `temperature_threshold`. The schema-less nature of DynamoDB allows adding new sensor fields (RPM, noise level) without table migration.

## JSON payload

```json
{
  "motor_id": "N20",
  "temperature": 27.78,
  "activation_time_ms": 500000,
  "timestamp": "2026-04-10T14:30:00Z"
}
```

- `motor_id` self-describing; robust against topic routing changes
- `temperature` Steinhart-Hart converted value in °C
- `activation_time_ms` Arduino `millis()` for sequencing and restart detection
- `timestamp` UTC, injected by the Python bridge (earliest point with a real clock)

## IAM design

Each Lambda has its own IAM role scoped to the minimum required permissions:

| Lambda | Permissions |
|---|---|
| writer | `dynamodb:PutItem` on `motor-metrics` |
| reader | `dynamodb:Query` on `motor-metrics` |
| config | `dynamodb:GetItem` + `dynamodb:PutItem` on `motor-metrics` |
| alerter | `dynamodb:GetItem` on `motor-metrics`, `sns:Publish` on `motor-alerts` |

## Project structure

```
├── thermistor_sketch
│   └── thermistor_sketch.ino    # Arduino sketch (Steinhart-Hart, JSON serial output)
├── bridge.py                # Python bridge (serial → MQTT, timestamp injection)
├── dashboard.html           # Live dashboard (Chart.js, hosted on S3/CloudFront)
├── lambda/
│   ├── writer.py            # IoT Rule → DynamoDB
│   ├── reader.py            # API Gateway → DynamoDB query
│   ├── config.py            # Dashboard config (GET/PUT threshold)
│   └── alerter.py           # Threshold check → SNS
├── docs/
│   └── architecture.svg     # Architecture diagram
└── certs/                   # AWS IoT X.509 certificates (not committed)
└── venv/                    # Virtual environment for Python 3.12

## Setup

Prerequisites: AWS account, Arduino Uno, NTC thermistor (22kΩ), Python 3.x with `pyserial` and `paho-mqtt`.

1. Flash `thermistor_sketch.ino` to the Arduino
2. Create an IoT Thing in AWS IoT Core and download certificates to `certs/`
3. Deploy Lambda functions and create IoT Rules (see architecture diagram for wiring)
4. Create API Gateway routes (`GET /metrics`, `GET /config`, `PUT /config`, `OPTIONS /config`)
5. Upload `dashboard.html` to S3 and configure CloudFront with OAC

All resources are in `eu-north-1` and stay within the permanent AWS Free Tier.

## Roadmap

- [ ] Run motor under load and capture real thermal anomalies
- [ ] Add RPM sensor (optical encoder) and microphone (ECM60)
- [ ] Per-sensor sampling rates (temperature: 30s, RPM/audio: faster)
- [ ] Time series analysis with tsfresh for anomaly detection
- [ ] Migrate dashboard to React
- [ ] Infrastructure as Code (Terraform or CloudFormation)
- [ ] Replace PC bridge with ESP32 for direct WiFi/MQTT connectivity
