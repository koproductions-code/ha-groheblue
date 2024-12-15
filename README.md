# HA GroheBlue

This is a HomeAssistant integration to interact with Grohe Blue Home devices. It is fairly new but functional. If you encounter any bugs, feel free to create an issue. 

## Disclaimer
I am not affiliated with Grohe or the Grohe app in any way. The integration is based on the python-package called "groheblue", which is based on the undocumented Grohe-API. If Grohe decides to change the API in any way, this could break the integration. Even tough I tested this integration with my device for several weeks without any malfunction, I am not liable for any potential issues, malfunctions, or damages arising from using this integration. Use at your own risk!

## Installation
1. Open the HACS panel in your Home Assistant frontend.
2. Navigate to the "Integrations" tab.
3. Click the three dots in the top-right corner and select "Custom Repositories."
4. Add a new custom repository:
    - URL: https://github.com/koproductions-code/ha-groheblue
    - Category: Integration
7. Click "Save" and then click "Install" on the Grohe Blue integration.
8. Then, restart your HomeAssistant Instance and go to Settings -> Devices & Services -> Add Integration and search for "Grohe Blue".
9. Enter your Grohe credentials and click on "Submit".

## Usage

### Options:
You can set the polling interval of integration manually in the "Configure" menu of the integration. Be aware that there might be limits with the Grohe API how often one can ask for new data. In my testing, a polling interval of 300 seconds seemed to work best. 

### This integration offers:
- [x] All sensor readings that are available from the api
- [x] Service action to dispense water  
- [x] Custom service action to reset filter & CO2, execute auto flush etc.


## License
This project is licensed under the <MIT> [MIT](https://github.com/koproductions-code/ha-groheblue/blob/master/LICENSE) license.

## Contact
If you encounter any bugs or have a request for a feature, feel free to create an issue on GitHub.
