# Security Analysis: MoMo SMS REST API

## 1. Introduction

A REST API exposes data to anyone who knows the URL. Without security, anyone could read or modify our SMS transactions. API security has two parts: **authentication** (who you are) and **authorization** (what you can do).

## 2. How Basic Authentication Works 

Every request must include an `Authorization: Basic <encoded>` header. The encoded part is `username:password` in Base64. The server decodes it, checks the credentials against values in `.env`, and either:

- Allows the request (returns 200/201)
- Returns **401 Unauthorized** if credentials are missing or wrong
- Returns **403 Forbidden** if credentials are valid but the user lacks permission (e.g., a `viewer` trying to DELETE)

## 3. Why Basic Auth Is Weak

Basic Authentication has serious weaknesses that make it a poor choice for any system handling sensitive data. These weaknesses fall into three categories: the encoding itself, repeated transmission, and the absence of session controls.

**Encoding is not protection.** Base64 was designed to make data safe to put inside HTTP headers, not to hide it. Decoding it requires no key, no skill, and no special tools — a single command does the job. In our own server, the encoded string `YWRtaW46cGFzc3dvcmQxMjM=` converts straight back to `admin:password123`. From a security standpoint, sending credentials in Base64 is essentially the same as sending them in plain text.

**Credentials travel with every request.** Token-based schemes ask for a password once at login and then use a short-lived token for everything else. Basic Auth does the opposite: every single request carries the full username and password. The more requests a user makes, the more opportunities an attacker has to intercept them. The credentials also tend to sit in the browser's local cache for the duration of the session, which means an attacker who gains access to the device — through malware, theft, or a shared machine — can pull them out without even watching the network.

**There is no concept of a session.** Basic Auth does not support logging out, does not expire, and does not lock accounts after failed attempts. A leaked password remains valid forever unless an administrator manually changes it, and changing it affects every user who shares those credentials. Brute-force attempts also go unchecked at the protocol level — the server has to add its own protection on top, because Basic Auth offers none.

A common defense is that HTTPS solves these problems. It is true that HTTPS prevents an outsider from reading the `Authorization` header in transit. But the threats above are not all about the network. HTTPS does nothing about cached credentials on the user's machine. It does nothing about the lack of expiration or logout. It does nothing if the server itself is compromised, or if Basic Auth is the only protection layer when something else is needed. According to the Cyber Advisors analysis, even when SSL is in use, Basic Authentication remains flawed because of these missing controls. HTTPS is a baseline, not a fix.

> **Source:** B. DeWall, *Simple Security Fails: part 5 – Basic Authentication*, Cyber Advisors, Sep 2024 — https://blog.cyberadvisors.com/technical-blog/simple-security-fails-part-5-basic-authentication


## 4. Stronger Alternative: JWT

According to Descope's comparison of authentication methods, JSON Web Token (JWT)-based authentication offers a more modern alternative to basic auth by issuing a signed token after login, rather than sending credentials with every request.  The key difference is *when* the credentials get exchanged. With Basic Auth, the username and password travel with every single request. With JWT, the user logs in once, the server verifies them once, and from then on the client only sends a token.

A JWT is made of three parts joined by dots: `header.payload.signature`. The **header** declares the signing algorithm. The **payload** holds claims about the user — things like user ID, role, and an expiration timestamp. The **signature** is created by cryptographically signing the header and payload with a secret key, which means the token cannot be altered without failing signature verification. 

This design addresses several Basic Auth weaknesses directly:

- **Reduced credential exposure.** The password is sent exactly once at login, not on every request.
- **Built-in expiration.** Tokens include an `exp` claim, so a stolen token stops working after a set time window (e.g., one hour).
- **Tamper resistance.** The cryptographic signature makes it impossible to forge or modify a valid token without the server's secret key.
- **Stateless validation.** The server verifies tokens locally using the signing key, with no database lookup required, which scales much better than Basic Auth's repeated credential checks.

In practice, a JWT request header looks like `Authorization: Bearer <token>` instead of `Authorization: Basic <encoded>`, and the rest of the API design stays similar. The added complexity (a login endpoint, signing-key management, secure client-side storage) is the main trade-off — but for any production system that handles sensitive data like mobile money transactions, this complexity is worth it.

> Source: Descope, *Basic vs. JWT-Based Authentication: What's the Difference?* — https://www.descope.com/blog/post/basic-vs-jwt


## 5. Stronger Alternative: OAuth2

OAuth 2.0 takes a different approach from both Basic Auth and JWT. According to the official OAuth specification, it is the industry-standard protocol for *authorization* rather than authentication — meaning it answers the question "what is this app allowed to do?" rather than "who is this user?" (oauth.net). The most familiar example is the "Sign in with Google" or "Sign in with GitHub" button — when you click it, your password never touches the third-party app. Google handles the login and gives the app a token instead.

Auth0's documentation describes OAuth as a framework that lets a user grant a third-party application access to their protected resources *without revealing their long-term credentials or identity*. This is the key difference from Basic Auth, where the credentials themselves are the access mechanism.

OAuth 2.0 brings several advantages:

- **Passwords stay with the trusted provider.** The application you're using never sees your password — only Google, GitHub, or whichever identity provider you chose.
- **Scopes provide granular permissions.** A backup app can be authorized to *read* your files but not delete them. Basic Auth has no concept of partial permissions.
- **Tokens are revocable.** You can disconnect an app from your Google account anytime, instantly cutting off its access — without changing your password.
- **Refresh tokens enable long sessions safely.** Instead of asking for your password again every hour, the app exchanges a long-lived refresh token for short-lived access tokens.

OAuth is more complex to implement than JWT — it requires an authorization server, redirect flows, and token management — so it is typically chosen when an application needs to integrate with external identity providers or expose its own API to third-party apps.

> **Sources:**
> - *OAuth 2.0*, oauth.net — https://oauth.net/2/
> - *OAuth 2.0 Authorization Framework*, Auth0 Docs — https://auth0.com/docs/authenticate/protocols/oauth

## 6. Improvements Implemented in This Project

While Basic Auth was the assigned scheme, the following improvements address some of its weaknesses:

| Improvement | Weakness Addressed |
|---|---|
| Credentials stored in `.env` (excluded from git via `.gitignore`) | Prevents accidental credential leaks in source code |
| Role-based access control (`admin` vs `viewer`, returns 403) | Limits damage if `viewer` credentials are compromised |
| `WWW-Authenticate` header on 401 responses | RFC 7235 compliance — clients know how to authenticate |
| Logging of failed auth attempts (`auth_failures.log`, no passwords logged) | Enables detection of brute-force attacks |

## 7. Conclusion

Basic Authentication is **easy to implement** and **acceptable for academic projects or internal tools behind HTTPS**, but it should never be used as the sole security mechanism in production. For real systems handling sensitive data like mobile money transactions, **JWT (with HTTPS)** is the minimum acceptable approach, with **OAuth2** preferred when integrating with external identity providers