# Automated classification of pre-defined movement patterns: A comparison between GNSS and UWB technology

In this repository, we exlore the characteristics of both a GNSS and UWB localisation system in correctly classifying pre-defined movement patterns. The automated framework, including experiment design, data collection, data pre-processing and data analyis is covered in this repository.

## Collecting UWB data

Once we have followed the several steps to correctly set up the Pozyx Creator System [1], we are ready to collect positioning data. In order to extract the data out of the UWB system, we can use the Python script [log_data.py](collecting_data/log_data.py), adapted from Pozyx [2]. If we prefer to have the data on a local device, we can create a direct connection by setting the variable named HOST to "localhost". On the other hand, a cloud connection can be established via a secure key. Within the Pozyx Creator Controller, we can generate a secure key by going to Settings -> API Keys. Additionally, we need to change the following variables: set HOST to "mqtt.cloud.pozyxlabs.com", change PORT to "443", set USERNAME and PASSWORD to the corresponding account. For more information, please visit [3]. Furthermore, within the [log_data.py](collecting_data/log_data.py) file, we can adjust the DURATION variable to the preferred amount of seconds we would like to collect data. 
Happy data collection!

[1]: https://docs.pozyx.io/creator/getting-started
[2]: https://docs.pozyx.io/enterprise/logging-data-from-the-mqtt-stream
[3]: https://docs.pozyx.io/creator/connect-with-mqtt

Disclaimer: this repository is currently under development. 

