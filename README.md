# PostNord Mail Delivery

![](https://img.shields.io/github/v/release/ticstyle/PostNord-Mail-Delivery?style=for-the-badge&color=blue)
![](https://img.shields.io/badge/Home%20Assistant-Custom%20Integration-blue?style=for-the-badge&logo=home-assistant)
![](https://img.shields.io/github/license/ticstyle/PostNord-Mail-Delivery?style=for-the-badge)
![](https://img.shields.io/github/downloads/ticstyle/PostNord-Mail-Delivery/total?style=for-the-badge&color=green)
![](https://img.shields.io/github/issues/ticstyle/PostNord-Mail-Delivery?style=for-the-badge&color=orange)[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

An asynchronous Home Assistant custom integration to track your next scheduled mail delivery from PostNord in Sweden.

To add this integration, please add the custom repository `https://github.com/ticstyle/PostNord-Mail-Delivery/` to HACS in your Home Assistant setup.

## 🌐 Supported Languages / Språk
The integration automatically handles translations natively under the hood. It exposes dedicated sensors for both Swedish and English text status outputs simultaneously, allowing you to force Swedish display texts even if your global Home Assistant profile language is set to English.

## ✨ Features
* **Device-Centric Architecture:** Instead of burying data inside attributes, the integration generates a clean Device element inside Home Assistant containing 5 dedicated, high-level sensors.
* **Automation-Friendly Core:** The primary days sensor returns a raw numeric integer (`0` for today, `1` for tomorrow), making automation conditions dead simple.
* **Dashboard Ready:** Native sensors mean you can add tracking elements directly to your Lovelace UI using standard entity cards—no advanced Jinja templates required.
* **100% Async & Safe:** Fully optimized using Home Assistant executor threads to prevent blocking the main event loop during file operations.

## 🚀 Installation

[![](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=ticstyle&repository=PostNord-Mail-Delivery&category=Integration)

Via [HACS](https://hacs.xyz/) or manually copy the `postnord_mail_delivery` folder from the [latest release](https://github.com/ticstyle/PostNord-Mail-Delivery/releases/latest) to the `custom_components` folder inside your Home Assistant configuration directory.

## ⚙️ Configuration

[![](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=postnord_mail_delivery)

Add the integration via the Home Assistant User Interface. You can set up multiple instances to track different postal codes simultaneously.

## 📊 Available Entities
When configuring a postal code (e.g., `11122`), the integration automatically registers a device named **PostNord 111 22** containing the following 5 entities:

| Entity ID | Name in UI | State Example | Description |
| :--- | :--- | :--- | :--- |
| `sensor.postnord_mail_delivery_11122` | Days until delivery | `1` | Raw days left until next delivery. Perfect for automations. |
| `sensor.postnord_mail_delivery_11122_friendly_status_en` | Friendly Status (EN) | `Tomorrow` | English relative status phrase (`Today`, `Tomorrow`, `In X days`). |
| `sensor.postnord_mail_delivery_11122_friendly_status_sv` | Friendly Status (SV) | `I morgon` | Swedish relative status phrase (`I dag`, `I morgon`, `Om X dagar`). |
| `sensor.postnord_mail_delivery_11122_next_delivery` | Next Delivery | `2026-07-03` | Explicit date string formatted as `YYYY-MM-DD`. |
| `sensor.postnord_mail_delivery_11122_postal_city` | Postal City | `Stockholm` | The verified city destination from the PostNord register. |

### Entity Attributes
Every single entity listed above also exposes the following common tracking metadata attributes:
* `last_update`: Formatted timestamp (`YYYY-MM-DD HH:MM:SS`) of the last API check.
* `postal_code`: Cleanly formatted tracking zone representation (e.g., `111 22`).

## 💡 Lovelace Dashboard Example
Because all data points are now first-class sensors, building a beautiful markdown summary layout is incredibly clean and no longer requires attribute lookups. Replace `11122` with your targeted postal code:

```yaml
type: markdown
title: "PostNord Postutdelning"
content: >
  Nästa postutdelning är: **{{ states('sensor.postnord_mail_delivery_11122_friendly_status_sv') }}**
  
  Exakt datum: {{ states('sensor.postnord_mail_delivery_11122_next_delivery') }}  
  Ort: {{ states('sensor.postnord_mail_delivery_11122_postal_city') }}
