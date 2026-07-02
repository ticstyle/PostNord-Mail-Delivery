# PostNord Mail Delivery
Swedish PostNord Mail Delivery integration for Home Assistant. 

This integration tracks your upcoming mail delivery days automatically based on your postal code.

## Installation

[![](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=ticstyle&repository=PostNord-Mail-Delivery&category=Integration)

Via [HACS](https://hacs.xyz/) or manually copy the `postnord_mail_delivery` folder from the [latest release](https://github.com/ticstyle/PostNord-Mail-Delivery/releases/latest) to the `custom_components` folder in your Home Assistant config directory.

## Configuration

[![](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=postnord_mail_delivery)

Add the integration via the Home Assistant UI. You can set up multiple instances if you want to track different postal codes.

---

## Sensor & Attributes

The primary sensor state shows the **number of days left** until your next mail delivery (e.g., `0`, `1`, `2`), which makes building automation rules incredibly simple. 

For frontend dashboards, the sensor exposes several helpful attributes that adapt dynamically to your Home Assistant language settings (supporting English and Swedish):

| Attribute | Type | Description | Example (EN / SV) |
|---|---|---|---|
| `friendly_status` | String | A human-readable translation of the delivery timeline. | `Tomorrow` / `I morgon` |
| `next_delivery` | String | The actual calendar date for the next delivery. | `2026-07-03` |
| `postal_city` | String | The city bound to the postal code. | `Stockholm` |
| `postal_code` | String | The configured postal code for the sensor instance. | `11122` |
| `last_update` | String | Timestamp of the last successful API poll. | `2026-07-02 14:00` |

### Frontend Example
You can easily extract the text state in a Markdown Card on your dashboard using this template:
```yaml
type: markdown
content: >
  Next PostNord delivery is: **{{ state_attr('sensor.postnord_mail_delivery_11122', 'friendly_status') }}**
