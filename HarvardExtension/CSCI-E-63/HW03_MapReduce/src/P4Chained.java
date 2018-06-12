package pkg;

import java.io.IOException;
import java.util.Arrays;
import java.util.StringTokenizer;

import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;
import org.apache.hadoop.mapreduce.lib.input.KeyValueTextInputFormat;
import org.apache.hadoop.conf.Configured;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.util.GenericOptionsParser;
import org.apache.hadoop.util.Tool;
import org.apache.hadoop.util.ToolRunner;


public class P4Chained extends Configured implements Tool {

	// NOTE: "I" moved to separate check
	public static final String[] STOP_WORDS = new String[] {"a","about","an","are","as","at","be","by","com","for","from","how",
			"in","is","it","of","on","or","that","the","this","to","was","what","when","where","who","will","with","the","www"
	};
	
	public static class TokenizerMapper 
       extends Mapper<Object, Text, Text, IntWritable>{
    
    private final static IntWritable one = new IntWritable(1);
    private Text word = new Text();
      
    public void map(Object key, Text value, Context context
                    ) throws IOException, InterruptedException {
        
      StringTokenizer itr = new StringTokenizer(value.toString());
      
      while (itr.hasMoreTokens()) {
    	String rawText = itr.nextToken();
    	//perhaps overly-harsh regex, e.g will remove hyphens from middle of words
    	String cleanWord = rawText.replaceAll("[^A-Za-z0-9 ]", "");
    	
        boolean isFirstPersonPronoun = cleanWord.equals(new String("I"));
    	if (!Arrays.asList(STOP_WORDS).contains(cleanWord.toLowerCase()) 
                && !isFirstPersonPronoun
                && cleanWord.length() > 0) {
            word.set(cleanWord);
            
            context.write(word, one);    		
    	}
      }
    }
  }


  public static class IntSumReducer 
       extends Reducer<Text,IntWritable,Text,IntWritable> {
    private IntWritable result = new IntWritable();

    public void reduce(Text key, Iterable<IntWritable> values, 
                       Context context
                       ) throws IOException, InterruptedException {
      int sum = 0;
      for (IntWritable val : values) {
        sum += val.get();
      }
      result.set(sum);
      context.write(key, result);
    }
  }

  
//P3Counter MapClass, updated to new API
  public static class MapClass 
  extends Mapper<Text, Text, IntWritable, Text>{

      public void map(Text key, Text value, Context context) throws IOException, InterruptedException  {
                 
      Integer rawCount = Integer.parseInt(value.toString());
      IntWritable count = new IntWritable(rawCount);
     
      context.write(count, key);
      } 
    }
  
  //P3Counter Reduce, updated to new API
  public static class Reduce extends Reducer<IntWritable, Text, IntWritable, IntWritable> {
      
      private IntWritable result = new IntWritable();
  
      public void reduce(IntWritable key, Iterable<Text> values,
                 Context context ) throws IOException, InterruptedException {
          
          int sum = 0;
          for(Text val : values) {
             sum++;
          }

          result.set(sum);
          context.write(key, result);
      }
  }
 
   
  private Job createP1Job(Configuration conf, Path in, Path out)
          throws IOException {
                
          Job job = Job.getInstance(conf, "P4Chained");

          job.setJobName("job1");
          job.setJarByClass(P4Chained.class);
          job.setMapperClass(TokenizerMapper.class);
          job.setCombinerClass(IntSumReducer.class);
          job.setReducerClass(IntSumReducer.class);   

          job.setOutputKeyClass(Text.class);
          job.setOutputValueClass(IntWritable.class);         

          FileInputFormat.setInputPaths(job, in);
          FileOutputFormat.setOutputPath(job, out);
          
          return job;
      }

  private Job createP3Job(Configuration conf, Path in, Path out)
          throws IOException {
                
          Job job = Job.getInstance(conf, "P4Chained");

          job.setJobName("job2");
          job.setJarByClass(P4Chained.class);
          job.setMapperClass(MapClass.class);
          job.setReducerClass(Reduce.class);          
          
          job.setInputFormatClass(KeyValueTextInputFormat.class);                
          //map emits diff key/value types vs. reduce
          job.setMapOutputKeyClass(IntWritable.class);
          job.setMapOutputValueClass(Text.class);
          job.setOutputKeyClass(IntWritable.class);
          job.setOutputValueClass(IntWritable.class);
          
          FileInputFormat.setInputPaths(job, in);
          FileOutputFormat.setOutputPath(job, out);

          conf.set("mapreduce.input.keyvaluelinerecordreader.key.value.separator", "\t");          
          
          return job;
      }


  public int run(String[] args) throws Exception, IOException {
      Configuration conf = new Configuration();
      String[] otherArgs = new GenericOptionsParser(conf, args).getRemainingArgs();
      
      Path in = new Path(otherArgs[0]);
      Path out = new Path(otherArgs[1]);
      Path temp = new Path("chain-temp");
      
      Job job1 = createP1Job(conf, in, temp);
      Integer job1Result = job1.waitForCompletion(true) ? 0 : 1;

      Job job2 = createP3Job(conf, temp, out);
      System.exit(job2.waitForCompletion(true) ? 0 : 1);
      
      //comment out during DEBUG
      cleanup(temp, conf);
      
      return 0;
  }

  
  private void cleanup(Path temp, Configuration conf)
          throws IOException {
           FileSystem fs = temp.getFileSystem(conf);
           fs.delete(temp, true);
       } 

  public static void main(String[] args) throws Exception { 
      int res = ToolRunner.run(new Configuration(), new P4Chained(), args);
      
      System.exit(res);
  }


}
