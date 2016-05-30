#! /bin/bash

TEMP_FILE_PROCESS=tmp_process.log
TEMP_FILE_TOTAL=performance_tests.log

function run {
    d=`date +%Y-%m-%d:%H:%M:%S`
    python -W ignore $1 $2 $3 $4 > $TEMP_FILE_PROCESS
    t=$(cat $TEMP_FILE_PROCESS | grep "Elapsed")
    n=$(cat $TEMP_FILE_PROCESS | grep "Normal")
    rm -rf $TEMP_FILE_PROCESS
    echo "$d; $3 $p; $t; $n"
    echo "$d; $3 $p; $t; $n" >> $TEMP_FILE_TOTAL
}

run -W ignore 1_1-GridSize.py 11
run -W ignore 1_1-GridSize.py 101
run -W ignore 1_1-GridSize.py 1001
run -W ignore 1_2-LayerNumbers.py 10
run -W ignore 1_2-LayerNumbers.py 100
run -W ignore 1_2-LayerNumbers.py 1000
run -W ignore 1_3-InactActCells.py 0
run -W ignore 1_3-InactActCells.py 50
run -W ignore 1_3-InactActCells.py 100
run -W ignore 1_4-HydralicConductivities.py 0
run -W ignore 1_4-HydralicConductivities.py 100
run -W ignore 1_4-HydralicConductivities.py 10000
run -W ignore 1_5-StorageCapacities.py 0
run -W ignore 1_5-StorageCapacities.py 1
run -W ignore 1_5-StorageCapacities.py 2
run -W ignore 2_1-StressPeriodsNumber.py 1
run -W ignore 2_1-StressPeriodsNumber.py 50
run -W ignore 2_1-StressPeriodsNumber.py 100
run -W ignore 2_2-TimeStepsNumber.py 10
run -W ignore 2_2-TimeStepsNumber.py 100
run -W ignore 2_2-TimeStepsNumber.py 1000
run -W ignore 2_3-TimeStepsLength.py 1
run -W ignore 2_3-TimeStepsLength.py 100
run -W ignore 2_3-TimeStepsLength.py 10000
run -W ignore 2_4-RiverStage.py 0
run -W ignore 2_4-RiverStage.py 100
run -W ignore 2_4-RiverStage.py 1000
run -W ignore 2_5-RiverConductance.py 0
run -W ignore 2_5-RiverConductance.py 100
run -W ignore 2_5-RiverConductance.py 10000
run -W ignore 2_6-WellsNumbers.py 1
run -W ignore 2_6-WellsNumbers.py 2
run -W ignore 2_6-WellsNumbers.py 3
run -W ignore 2_7-PumpingRates.py 3 -100
run -W ignore 2_7-PumpingRates.py 3 -1000
run -W ignore 2_7-PumpingRates.py 3 -10000
run -W ignore 2_8-RechargeData.py 0
run -W ignore 2_8-RechargeData.py 10
run -W ignore 2_8-RechargeData.py 100
run -W ignore 2_9-GHB.py 0
run -W ignore 2_9-GHB.py 1
run -W ignore 3_1-Packages.py 1
run -W ignore 3_1-Packages.py 2
run -W ignore 3_2-Laycon.py 1
run -W ignore 3_2-Laycon.py 2
run -W ignore 3_2-Laycon.py 3

