# streamdiff

A CLI tool to diff and validate schema changes in Kafka and Kinesis streams.

## Installation

```bash
pip install streamdiff
```

## Usage

Compare schema versions across streams:

```bash
# Diff two Kafka topics
streamdiff kafka --broker localhost:9092 --topic orders-v1 --topic orders-v2

# Validate a Kinesis stream against a schema file
streamdiff kinesis --stream my-stream --schema schema.json

# Output diff in JSON format
streamdiff kafka --broker localhost:9092 --topic events-v1 --topic events-v2 --output json
```

Example output:

```
Schema diff: orders-v1 → orders-v2
  + added:   customer_id (string)
  ~ changed: amount (int → float)
  - removed: legacy_code (string)

2 breaking changes detected.
```

### Supported Backends

| Backend  | Diff | Validate |
|----------|------|----------|
| Kafka    | ✅   | ✅       |
| Kinesis  | ✅   | ✅       |

## Configuration

Set credentials via environment variables or a `.streamdiff.yml` config file:

```bash
export KAFKA_BROKER=localhost:9092
export AWS_REGION=us-east-1
```

## Contributing

Pull requests are welcome. Please open an issue first to discuss proposed changes.

## License

[MIT](LICENSE)