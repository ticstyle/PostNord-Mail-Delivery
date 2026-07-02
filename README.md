# PostNord Mail Delivery

![](https://img.shields.io/github/v/release/ticstyle/PostNord-Mail-Delivery?style=for-the-badge&color=blue)
![](https://img.shields.io/badge/Home%20Assistant-Custom%20Integration-blue?style=for-the-badge&logo=home-assistant)
![](https://img.shields.io/github/license/ticstyle/PostNord-Mail-Delivery?style=for-the-badge)
![](https://img.shields.io/github/downloads/ticstyle/PostNord-Mail-Delivery/total?style=for-the-badge&color=green)
![](https://img.shields.io/github/issues/ticstyle/PostNord-Mail-Delivery?style=for-the-badge&color=orange)

An asynchronous Home Assistant custom integration to track your next scheduled mail delivery from PostNord in Sweden.

To add this integration, please add the custom repository `https://github.com/ticstyle/PostNord-Mail-Delivery/` to HACS in your Home Assistant setup.

## 🌐 Supported Languages / Språk
The integration automatically detects your Home Assistant user profile settings and localizes all configurations and attributes dynamically:
* 🇸🇪 **Svenska** (Fullt stöd för gränssnitt och attribut)
* 🇬🇧 **English** (Full UI and attribute localization)

## ✨ Features
* **Automation-Friendly State:** The primary sensor state returns a raw numeric integer representing the days remaining until your next delivery (`0` for today, `1` for tomorrow, etc.), making automation logic dead simple.
* **On-the-fly Localization:** No hardcoded strings. Translations are handled natively via `strings.json` and `sv.json`.
* **Rich Attributes:** Exposes detailed metadata directly into the sensor attributes for advanced card layouts.

## 🚀 Installation

[![](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=ticstyle&repository=PostNord-Mail-Delivery&category=Integration)

Via [HACS](https://hacs.xyz/) or manually copy the `postnord_mail_delivery` folder from the [latest release](https://github.com/ticstyle/PostNord-Mail-Delivery/releases/latest) to the `custom_components` folder inside your Home Assistant configuration directory.

## ⚙️ Configuration

[![](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=postnord_mail_delivery)

Add the integration via the Home Assistant User Interface. You can set up multiple instances to track different postal codes simultaneously.

## 📊 Sensor Attributes
The main sensor exposes several useful `extra_state_attributes` which can be pulled into Markdown or custom cards:

| Attribute | Description | Example (EN) | Example (SV) |
| :--- | :--- | :--- | :--- |
| `friendly_status` | A localized, human-readable status phrase | `Tomorrow` | `I morgon` |
| `next_delivery` | The confirmed date of the next delivery | `2026-07-03` | `2026-07-03` |
| `postal_city` | The city mapped to your postal code | `Stockholm` | `Stockholm` |
| `postal_code` | The monitored postal code | `11122` | `11122` |
| `last_update` | Timestamp of the last API refresh | `2026-07-02 14:55` | `2026-07-02 14:55` |

## 💡 Lovelace Dashboard Example
You can use the built-in `friendly_status` attribute to build a clean Markdown card on your dashboard. Replace `11122` with your postal code:

```yaml
type: markdown
title: "PostNord Postutdelning"
content: >
  Nästa postutdelning är: **{{ state_attr('sensor.postnord_mail_delivery_11122', 'friendly_status') }}**
  
  Exakt datum: {{ state_attr('sensor.postnord_mail_delivery_11122', 'next_delivery') }}  
  Ort: {{ state_attr('sensor.postnord_mail_delivery_11122', 'postal_city') }}
