# Crestron HD-MD4x1-4K-E HDMI Matrix

This integration communicates with the Crestron **HD-MD4x1-4K-E** HDMI matrix over Telnet. It exposes a `select` entity that allows choosing the input routed to output 1 and listens for routing events from the device.

## Custom installation

Copy the folder `crestron_hdmi_matrix` into the `custom_components` directory of your Home Assistant installation. Restart Home Assistant and add the **Crestron HD‑MD4x1‑4K‑E HDMI Matrix** integration from the UI. You will be asked for the IP address of the device. After configuration, a select entity named **HDMI Output 1 Source** will appear.

## Official integration

When submitting this integration to Home Assistant core, move the directory under `homeassistant/components` and add tests and documentation accordingly.
