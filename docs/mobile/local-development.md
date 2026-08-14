# Mobile Local Development

The Flutter app receives the Django API base URL with `--dart-define`.

```bash
flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8000
```

## Android Emulator

Use:

```text
http://10.0.2.2:8000
```

`10.0.2.2` points from the Android emulator to the host machine.

## iOS Simulator

Use:

```text
http://127.0.0.1:8000
```

## Physical Device

Use the host machine IP on the same network:

```text
http://192.168.x.x:8000
```

The backend must listen on an address reachable by the device.

## Security

Plain HTTP is acceptable only for local development.

Production environments must use HTTPS.

Do not store API secrets in the Flutter app.

Do not disable TLS validation globally.
