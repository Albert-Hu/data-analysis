#!/bin/bash

link=https://data.moi.gov.tw/MoiOD/System/DownloadFile.aspx?DATA=19059799-9436-4D7D-8C5E-90F1A9CE82DA

mkdir raw_data
wget -O raw_data/data.zip $link
unzip raw_data/data.zip -d raw_data
