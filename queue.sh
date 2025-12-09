#!/bin/bash

set -e
# 定义清理和调度的函数
cleanup_and_next() {
    cd /data/liuyuan/FoldExplorer
    if [[ -z "$1" ]]; then
        # 如果 $1 是空，则删除 running.queue 中含 "None" 的行
        sed -i '/None/d' running.queue
    else
        # 否则正常删除匹配 $1 的行
        sed -i "/$1/d" running.queue
    fi
    # 检查 waiting.queue 中是否还有任务
    rowInfoNew=$(wc -l waiting.queue)
    rowNew=$(echo $rowInfoNew | awk '{print $1}')
    if [[ $rowNew -gt 0 ]]; then
        cmdLineNew=$(head -n 1 waiting.queue)
        p1=$(echo $cmdLineNew | awk '{print $2}')
        p2=$(echo $cmdLineNew | awk '{print $3}')
        p3=$(echo $cmdLineNew | awk '{print $4}')
        p4=$(echo $cmdLineNew | awk '{print $5}')
        p5=$(echo $cmdLineNew | awk '{print $6}')
        sed -i '1d' waiting.queue
        bash queue.sh $p1 $p2 $p3 $p4 $p5 > /data/liuyuan/FoldExplorer/temp.log 2>&1 &
    fi
}

# trap 保证无论中途是否出错，cleanup_and_next 一定会执行
job_id="$1"
trap 'cleanup_and_next "$job_id"' EXIT

cd /data/liuyuan/FoldExplorer
rowInfo=$(wc -l running.queue)
row=$(echo $rowInfo | awk '{print $1}')

if [[ $row -lt 2 ]]; then
    echo "./run $1 $2 $3 $4 $5" >> running.queue
    cd /data/liuyuan/FoldExplorer/program

    if [[ "$5" == "pdb" ]]; then
        ./run_from_pdb.sh $1 $2 $3 $4 $5
    elif [[ "$5" == "fasta" ]]; then
        ./run_from_fasta.sh $1 $2 $3 $4 $5
    elif [[ "$5" == "text" ]]; then
        ./run_from_text.sh $1 $2 $3 $4 $5
    else
        echo "Error: unknown input type $5"
        exit 1
    fi

else
    echo "./run $1 $2 $3 $4 $5" >> waiting.queue
fi
