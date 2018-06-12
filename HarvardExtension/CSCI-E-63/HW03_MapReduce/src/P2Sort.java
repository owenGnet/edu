package pkg;

import java.io.IOException;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;
import org.apache.hadoop.util.GenericOptionsParser;
import org.apache.hadoop.mapreduce.lib.input.KeyValueTextInputFormat;

import org.apache.hadoop.conf.Configured;
import org.apache.hadoop.util.Tool;
import org.apache.hadoop.util.ToolRunner;


public class P2Sort extends Configured implements Tool {

    public static class MapClass 
    extends Mapper<Text, Text, LongWritable, Text>{

      public void map(Text key, Text value, Context context) throws IOException, InterruptedException  {                  

          Long rawCount = Long.parseLong(value.toString());
          LongWritable count = new LongWritable(rawCount);
          
          context.write(count, key);
      } 
    }
    
    
    public static class Reduce extends Reducer<LongWritable, Text, Text, LongWritable> {
        
        public void reduce(LongWritable key, Text value,
                   Context context ) throws IOException, InterruptedException {

            context.write(value, key);
        }
    }
    

    public int run(String[] args) throws Exception {
        Configuration conf = getConf();
        conf.set("mapreduce.input.keyvaluelinerecordreader.key.value.separator", "\t");
        
        String[] otherArgs = new GenericOptionsParser(conf, args).getRemainingArgs();
        if (otherArgs.length < 2) {
          System.err.println("Usage: P5Inverter_newAPI <in> [<in>...] <out>");
          System.exit(2);
        }
        
        Job job = Job.getInstance(conf, "P5Inverter_newAPI");        
        job.setJarByClass(P2Sort.class);
        job.setMapperClass(MapClass.class);
        job.setReducerClass(Reduce.class);        
        
        job.setInputFormatClass(KeyValueTextInputFormat.class);
        
        job.setMapOutputKeyClass(LongWritable.class);
        job.setMapOutputValueClass(Text.class);
        job.setSortComparatorClass(LongWritable.DecreasingComparator.class);
        
        job.setOutputKeyClass(Text.class);
        job.setOutputValueClass(LongWritable.class);
        
        for (int i = 0; i < otherArgs.length - 1; ++i) {
          FileInputFormat.addInputPath(job, new Path(otherArgs[i]));
        }
        FileOutputFormat.setOutputPath(job,
          new Path(otherArgs[otherArgs.length - 1]));
        System.exit(job.waitForCompletion(true) ? 0 : 1);
        
        return 0;
      }
      
    
    public static void main(String[] args) throws Exception { 
        int res = ToolRunner.run(new Configuration(), new P2Sort(), args);
        
        System.exit(res);
    }
}
