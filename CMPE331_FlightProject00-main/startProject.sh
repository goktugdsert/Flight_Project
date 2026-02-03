{\rtf1\ansi\ansicpg1254\cocoartf2822
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 #!/bin/bash\
\
# Renkli \'e7\uc0\u305 kt\u305  i\'e7in (\u304 ste\u287 e ba\u287 l\u305 , Windows'taki color 0A benzeri)\
GREEN='\\033[0;32m'\
NC='\\033[0m' # No Color\
\
echo -e "$\{GREEN\}=========================================="\
echo "CMPE331 - BACKEND SERVISLERI BASLATILIYOR (macOS)"\
echo "=========================================="\
echo -e "$\{NC\}"\
\
# Fonksiyon: Komutu yeni bir Terminal penceresinde \'e7al\uc0\u305 \u351 t\u305 r\u305 r\
# Bu, Windows'taki "start cmd /k" komutunun kar\uc0\u351 \u305 l\u305 \u287 \u305 d\u305 r.\
open_terminal_tab() \{\
    osascript -e "tell application \\"Terminal\\" to do script \\"$1\\""\
\}\
\
# 1. FLIGHT & PASSENGER API (Port 8000)\
echo "[1/3] Flight API (Port 8000) aciliyor..."\
# Dikkat: Slashlar '/' oldu ve 'venv/bin/activate' kullan\uc0\u305 ld\u305 \
CMD1="cd passenger_flight/flight_info_project && source venv/bin/activate && python manage.py runserver 8000"\
open_terminal_tab "$CMD1"\
\
# 2. MAIN SYSTEM (Port 8001)\
echo "[2/3] Main System (Port 8001) aciliyor..."\
CMD2="cd Main_System && source venv/bin/activate && python manage.py runserver 8001"\
open_terminal_tab "$CMD2"\
\
# 3. CREW API (Port 8002)\
echo "[3/3] Crew API (Port 8002) aciliyor..."\
# Windows scriptindeki cd mant\uc0\u305 \u287 \u305  korundu\
CMD3="cd pilot_cabin && source venv/bin/activate && cd flight_roster_project && python manage.py runserver 8002"\
open_terminal_tab "$CMD3"\
\
echo -e "$\{GREEN\}=========================================="\
echo "TUM SISTEMLER AKTIF!"\
echo -e "==========================================$\{NC\}"}