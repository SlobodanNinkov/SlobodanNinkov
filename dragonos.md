---

layout: page

title: SDR & Cellular Signal Analysis — Lab Notes

subtitle: Practical tips and tricks for data extraction

---



DragonOS R37.1 cellular experiments





\# GSM



Check GSM cell:

grgsm\_livemon

Set GSM channel BCCH frequency in grgsm\_livemon



If the signal is strong enough to be decoded, it will start streaming pcap data.



sudo wireshark -k -Y ‘gsmtap’ -i lo



OpenBTS power control:

Strongest -> can burn out the output, I never used more than 3 3 for a few seconds. 10 10 is ok for a more extended period:

power 5 5 

Weakest:

power 80 80



config

devconfig

 





\# LTE



4G operation using RTLSDR (note that this does not work above 1.8MHz on RTLSDR):



CellSearch –freq-start 1845e6



LTE-Tracker -f 954.9e6



Find USRP devices, a good first check if a system is correctly configured:

uhd\_find\_devices



Sending a strictly defined signal using USRP:

uhd\_siggen



