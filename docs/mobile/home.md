# Mobile Home

## Role

The Home feature is the authenticated entry point for Health OS mobile.

It is intentionally small in this step. It gives authenticated users a stable first screen while future health modules are built.

## Current Content

The screen shows:

- generic greeting;
- `Seu Health OS` summary;
- quick access section;
- planned module cards;
- local logout action.

The Home does not load profile data, health data, measurements, goals, habits, exercise plans, recommendations, or AI content.

No fake user data is rendered.

## Planned Cards

The first planned cards are:

- Saude;
- Metas;
- Habitos;
- Exercicios.

They are marked as `Em breve` and do not navigate to unavailable modules.

## Auth Gate

`AuthGate` renders Home only when `SessionController` is authenticated.

Home receives only a logout callback. It does not read tokens, receive tokens as route arguments, or depend on authentication presentation internals.

## Logout

The current logout is local only:

1. clear `SessionStorage`;
2. update global authentication state;
3. return to Login.

Backend logout, token revocation, blacklist behavior, and definitive authenticated navigation are still future work.
