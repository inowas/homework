#! /bin/bash

TEMP_FILE_PROCESS=tmp_process.log
TEMP_FILE_TOTAL=performance_tests.log

function run {
    for i in {1..10}
    do
        d=`date +%Y-%m-%d:%H:%M:%S`
        python $1 $2 $3 > $TEMP_FILE_PROCESS
        t=$(cat $TEMP_FILE_PROCESS | grep "Elapsed")
        n=$(cat $TEMP_FILE_PROCESS | grep "Normal")
        rm -rf $TEMP_FILE_PROCESS
        PARAMETERS="$2; $3"
        echo "$d; $1; $PARAMETERS $p; $t; $n"
        echo "$d; $1; $PARAMETERS $p; $t; $n" >> $TEMP_FILE_TOTAL
    done
}

run 1_1-GridSize.py 11
run 1_1-GridSize.py 101
run 1_1-GridSize.py 1001
run 1_2-LayerNumbers.py 10
run 1_2-LayerNumbers.py 100
run 1_2-LayerNumbers.py 1000
run 1_3-InactActCells.py 0
run 1_3-InactActCells.py 50
run 1_3-InactActCells.py 100
run 1_4-HydralicConductivities.py 0
run 1_4-HydralicConductivities.py 100
run 1_4-HydralicConductivities.py 10000
run 1_5-StorageCapacities.py 0
run 1_5-StorageCapacities.py 1
run 1_5-StorageCapacities.py 2
run 2_1-StressPeriodsNumber.py 1
run 2_1-StressPeriodsNumber.py 50
run 2_1-StressPeriodsNumber.py 100
run 2_2-TimeStepsNumber.py 10
run 2_2-TimeStepsNumber.py 100
run 2_2-TimeStepsNumber.py 1000
run 2_3-TimeStepsLength.py 1
run 2_3-TimeStepsLength.py 100
run 2_3-TimeStepsLength.py 10000
run 2_4-RiverStage.py 0
run 2_4-RiverStage.py 100
run 2_4-RiverStage.py 1000
run 2_5-RiverConductance.py 0
run 2_5-RiverConductance.py 100
run 2_5-RiverConductance.py 10000
run 2_6-WellsNumbers.py 1
run 2_6-WellsNumbers.py 2
run 2_6-WellsNumbers.py 3
run 2_7-PumpingRates.py 3 -100
run 2_7-PumpingRates.py 3 -1000
run 2_7-PumpingRates.py 3 -10000
run 2_8-RechargeData.py 0
run 2_8-RechargeData.py 10
run 2_8-RechargeData.py 100
run 2_9-GHB.py 0
run 2_9-GHB.py 1
run 3_1-Packages.py 1
run 3_1-Packages.py 2
run 3_2-Laycon.py 1
run 3_2-Laycon.py 2
run 3_2-Laycon.py 3
run 4_1-Solver.py 1
run 4_1-Solver.py 2
run 4_1-Solver.py 3
run 4_1-Solver.py 4
run 4_1-Solver.py 5
