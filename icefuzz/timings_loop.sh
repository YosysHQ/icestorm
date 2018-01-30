while true; do
	rm -rf data_5k_*.txt work_5k_*
	make DEVICECLASS=5k -j3
	make DEVICECLASS=5k timings
done
