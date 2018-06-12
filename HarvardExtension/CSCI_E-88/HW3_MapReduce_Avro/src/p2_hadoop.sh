input_dir=/e88/A3/p2_input
output_dir=/e88/A3/p2_output
hdfs dfs -rmr $output_dir

STREAM_JAR=hadoop-streaming

$STREAM_JAR \
    -D mapred.reduce.tasks=1  \
    -mapper "$PWD/p2_mapper.py" \
    -reducer "$PWD/p2_reducer.py -q 1" \
    -input "$input_dir/" \
    -output "$output_dir"  \
    -file "$PWD/p2_mapper.py" \
    -file "$PWD/p2_reducer.py"
