input_dir=/e88/A3/p1_input
output_dir=/e88/A3/p1_output
hdfs dfs -rmr $output_dir

STREAM_JAR=hadoop-streaming

$STREAM_JAR \
    -D mapred.reduce.tasks=1  \
    -mapper "$PWD/p1_mapper.py" \
    -reducer "$PWD/p1_reducer.py -q 3 -d True" \
    -input "$input_dir/" \
    -output "$output_dir"  \
    -file "$PWD/p1_mapper.py" \
    -file "$PWD/p1_reducer.py"
