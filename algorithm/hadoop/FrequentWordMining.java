package FrequentWordMining;

import java.awt.print.Printable;
import java.io.IOException;
import java.io.InterruptedIOException;
import java.util.ArrayList;
import java.util.StringTokenizer;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;
import org.apache.hadoop.util.GenericOptionsParser;

public class FrequentWordMining {
	
	public static class FrequentWordMingMapper extends Mapper<Object, Text, Text, IntWritable>{
		private final static IntWritable one = new IntWritable(1);
		private Text word = new Text();
		private int min_frequentword_len = 4;
		
		@Override
		protected void map(Object key, Text value, Context context) throws IOException, InterruptedException{
			StringTokenizer itr = new StringTokenizer(value.toString());
			while(itr.hasMoreTokens()){
				String full_word = itr.nextToken();
				ArrayList<String> sub_words;
				try {
					sub_words = getSubstringList(full_word, min_frequentword_len);
					if(sub_words == null){
						continue;
					}
					for(int i = 0; i < sub_words.size(); ++i){
						word.set(sub_words.get(i));
						context.write(word, one);
					}
				} catch (Exception e) {
					e.printStackTrace();
				}
			}
		}
		
		private ArrayList<String> getSubstringList(String word, int k) throws Exception{
			if(k > word.length()){
				return null;
			}
			else {
				ArrayList<String> sub_words = new ArrayList<String>();
				for(int i = k; i < word.length(); ++i){
					for(int j = 0; j < word.length() - i; ++j){
						String sub_word = word.substring(j, j + i);
						sub_words.add(sub_word);
					}
				}
				return sub_words;
			}
		}
	}
	
	public static class FrequentWordMiningReducer extends Reducer<Text, IntWritable, Text, IntWritable>{
		private IntWritable result = new IntWritable();
		
		@Override
		protected void reduce(Text key, Iterable<IntWritable> values, Context context) throws IOException, InterruptedException {
			int sum = 0;
			for(IntWritable i: values){
				sum += i.get();
			}
			result.set(sum);
			context.write(key,result);
		}
	}
	
	public static void main(String[] args) throws Exception{
		Configuration conf = new Configuration();
		String[] otherArgs = new GenericOptionsParser(conf, args).getRemainingArgs();
		Job job = new Job(conf, "frequent word mining");
		job.setJarByClass(FrequentWordMining.class);
		job.setMapperClass(FrequentWordMingMapper.class);
		job.setCombinerClass(FrequentWordMiningReducer.class);
		job.setReducerClass(FrequentWordMiningReducer.class);
		job.setOutputKeyClass(Text.class);
		job.setOutputValueClass(IntWritable.class);
		
		FileInputFormat.addInputPath(job, new Path(otherArgs[0]));
		FileOutputFormat.setOutputPath(job, new Path(otherArgs[1]));
		System.exit(job.waitForCompletion(true)?0:1);
	}

}
