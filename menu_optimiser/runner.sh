

python3 temp_writer.py & PID1=$!
python3 light_writer.py & PID2=$!

sleep 16

kill $PID1 $PID2 2>/dev/null
echo "Collected logs"

LOG_DIR="/home/mahima/dev/Team_Ultra_UBH-2025/menu_optimiser/logs"

latest_temp=$(ls -t "$LOG_DIR"/temp_logs_* 2>/dev/null | head -1)
latest_lux=$(ls -t "$LOG_DIR"/lux_output_* 2>/dev/null | head -1)


echo "Latest temp: $latest_temp"
echo "Latest lux: $latest_lux"

python comp_prompter.py --temp_file $latest_temp --lux_file $latest_lux --menu_file logs/menu4.txt

echo "Recommonedaiton made"
