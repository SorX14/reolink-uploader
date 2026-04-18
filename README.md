# Reolink uploader

A small script that uploads provided certificates to Reolink cameras.

## Usage

Run with:

`uv run reolink-uploader {camera-name}`

Might need:

`uv sync` once.

## Setup

Camera names are listed in `.camera_credentials.json`.

Assumption is that certifications are stored in `../certs` e.g:

```
|- certs
|---- mydomain.example.com
|------- cert.pem
|------- key.pem
|- reolink_uploader
|---- README.md <- this file
```

## Ramblings

Can be used with any certificate provider as long as they exist in the `certs`. Originally used with OPNsense
and the ACME client plugin. Use an automation to SFTP your certificates to `/certs`, then trigger this
script with the camera name.

Not all Reolink cameras support uploading custom certificates - especially the older ones. This has worked with:

- CX810
- TrackMix PoE
- RLC-820A
- RLC-520A

## Acknowledgments

Used the update script from here: https://gist.github.com/velzend/895c18d533b3992f3a0cc128f27c0894