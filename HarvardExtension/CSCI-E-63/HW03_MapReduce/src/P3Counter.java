package pkg;

import java.io.IOException;
import java.util.Iterator;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.conf.Configured;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapred.FileInputFormat;
import org.apache.hadoop.mapred.FileOutputFormat;
import org.apache.hadoop.mapred.JobClient;
import org.apache.hadoop.mapred.JobConf;
import org.apache.hadoop.mapred.KeyValueTextInputFormat;
import org.apache.hadoop.mapred.MapReduceBase;
import org.apache.hadoop.mapred.Mapper;
import org.apache.hadoop.mapred.OutputCollector;
import org.apache.hadoop.mapred.Reducer;
import org.apache.hadoop.mapred.Reporter;
import org.apache.hadoop.mapred.TextOutputFormat;
import org.apache.hadoop.mapreduce.Reducer.Context;
import org.apache.hadoop.util.Tool;
import org.apache.hadoop.util.ToolRunner;

//NOTE: still in old API format
public class P3Counter extends Configured implements Tool {
    
    public static class MapClass extends MapReduceBase
        implements Mapper<Text, Text, IntWritable, Text> {
        
        public void map(Text key, Text value,
                        OutputCollector<IntWritable, Text> output,
                        Reporter reporter) throws IOException {
                        
        	Integer rawCount = Integer.parseInt(value.toString());
        	IntWritable count = new IntWritable(rawCount);
        	
            output.collect(count, key);
        }
    }
    
    public static class Reduce extends MapReduceBase
        implements Reducer<IntWritable, Text, IntWritable, IntWritable> {

        private IntWritable result = new IntWritable();
        
        public void reduce(IntWritable key, Iterator<Text> values,
                       OutputCollector<IntWritable, IntWritable> output,
                       Reporter reporter) throws IOException {

            int sum = 0;
            for ( ; values.hasNext(); ++sum ) values.next(); 

            result.set(sum);
            output.collect(key, result);
        }
    }

    
    public int run(String[] args) throws Exception {
        Configuration conf = getConf();
        
        JobConf job = new JobConf(conf, P3Counter.class);
        
        Path in = new Path(args[0]);
        Path out = new Path(args[1]);
        FileInputFormat.setInputPaths(job, in);
        FileOutputFormat.setOutputPath(job, out);
        
        job.setJobName("P3Counter");
        job.setMapperClass(MapClass.class);
        job.setReducerClass(Reduce.class);
        //map emits diff key/value types vs. reduce
        job.setMapOutputKeyClass(IntWritable.class);
        job.setMapOutputValueClass(Text.class);
        
        job.setInputFormat(KeyValueTextInputFormat.class);
        job.setOutputFormat(TextOutputFormat.class);
        
        job.setOutputKeyClass(IntWritable.class);
        job.setOutputValueClass(IntWritable.class);
        
        job.set("key.value.separator.in.input.line", "\t");
        
        JobClient.runJob(job);
        
        return 0;
    }
    
    public static void main(String[] args) throws Exception { 
        int res = ToolRunner.run(new Configuration(), new P3Counter(), args);
        
        System.exit(res);
    }
}
