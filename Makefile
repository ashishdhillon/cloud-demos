# Cloud Systems Engineering Labs - Master Makefile
.PHONY: help menu run start stop status web portal p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15

help:
	@echo "Cloud Systems Engineering Labs - Command Reference"
	@echo "----------------------------------------------------"
	@echo "  make web / portal - Launch interactive browser portal (:3000)"
	@echo "  make run        - Open interactive CLI lab menu"
	@echo "  make status     - View currently active lab"
	@echo "  make stop       - Stop any active lab and free port 8080"
	@echo "  make p<N>       - Launch Practical N directly (e.g. make p4, make p10)"
	@echo "----------------------------------------------------"

web portal:
	@./portal.sh

menu run:
	@./run.sh

status:
	@./run.sh status

stop down:
	@./run.sh stop

p1 practical-01:
	@./run.sh 1

p2 practical-02:
	@./run.sh 2

p3 practical-03:
	@./run.sh 3

p4 practical-04:
	@./run.sh 4

p5 practical-05:
	@./run.sh 5

p6 practical-06:
	@./run.sh 6

p7 practical-07:
	@./run.sh 7

p8 practical-08:
	@./run.sh 8

p9 practical-09:
	@./run.sh 9

p10 practical-10:
	@./run.sh 10

p11 practical-11:
	@./run.sh 11

p12 practical-12:
	@./run.sh 12

p13 practical-13:
	@./run.sh 13

p14 practical-14:
	@./run.sh 14

p15 practical-15:
	@./run.sh 15
