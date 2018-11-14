mpirun -display-map --verbose -map-by node -np 6 --mca oop_tcp_static_ports 8443 -mca plm_rsh_args "-p 8443" -machinefile /tmp/horovod3d/Code/keras/hostfile.txt python EcalEnergyTrain_hvd.py --datapath=/tmp/horovod3d/Data/EleEscan_*.h5 --batchsize 36 -lr 0.001 --optimizer=Adam --latentsize 200 --warmup 0 --nbepochs 30 --analysis=True 2>&1 | tee stdout.log