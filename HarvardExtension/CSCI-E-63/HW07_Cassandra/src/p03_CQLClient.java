package edu.hu.cassandra;

	import com.datastax.driver.core.Cluster;
	import com.datastax.driver.core.Host;
	import com.datastax.driver.core.Metadata;
	import com.datastax.driver.core.Session;
	import com.datastax.driver.core.ResultSet;
	import com.datastax.driver.core.Row;
	
	public class P03_CQLClient {
	   private Cluster cluster;
	   private Session session;
	   public static final String p03 = "p03";

	   public void connect(String node) {
	      cluster = Cluster.builder()
	            .addContactPoint(node).build();
	      session = cluster.connect();
	      Metadata metadata = cluster.getMetadata();
	      System.out.printf("Connected to cluster: %s\n", 
	            metadata.getClusterName());
	      for ( Host host : metadata.getAllHosts() ) {
	         System.out.printf("Datatacenter: %s; Host: %s; Rack: %s\n",
	               host.getDatacenter(), host.getAddress(), host.getRack());
	      }
	   }

	   public void createSchema() {		   
		   session.execute("CREATE KEYSPACE " + p03 + " WITH replication " + 
				      "= {'class':'SimpleStrategy', 'replication_factor':1};");
		   session.execute(
			   	"CREATE TABLE " + p03 + ".person (" +
			   			"person_id int PRIMARY KEY," +
			   			"fname text," +
			   			"lname text," +
			   			"city text," +
			   			"cell_phone set<text>);");

	   }

	   public void loadData() {
		   String insertPrefix = "INSERT INTO " + p03 + ".person " + 
				   		"(person_id, fname, lname, city, cell_phone) VALUES";
		   
		   session.execute(insertPrefix + 
			    "(1, 'Winston', 'Churchill', 'London', {'+44 20 7925 0918'});");
		   session.execute(insertPrefix + 
			   	"(2, 'Franklin', 'Roosevelt', 'Hyde Park', {'212-504-4115','202-456-1111','518-474-8390'});");
		   session.execute(insertPrefix + 
			   	"(3, 'Joseph', 'Stalin', 'Moscow', {'+7 495 697-03-49'});");

	   }
	   public void querySchema(){
		   ResultSet results = session.execute(
				   "SELECT fname, lname, city, cell_phone FROM " + p03 + ".person ");
		   System.out.println(String.format("%-15s\t%-15s\t%-15s\t%-15s\n%s",
					"fname", "lname", "city", "cell_phone",
					"-----------+----------------+----------------+---------------------------------"));
		   for (Row row : results) {
			    System.out.println(String.format("%-15s\t%-15s\t%-15s\t%-15s", 
			    	row.getString("fname"), row.getString("lname"), row.getString("city"), 
			    	row.getSet("cell_phone", String.class)));
		   }
			System.out.println();

	   }
	   
	   public void close() {
	      cluster.close(); // .shutdown();
	   }

	   public static void main(String[] args) {
		   
	      P03_CQLClient client = new P03_CQLClient();
	      client.connect("127.0.0.1");
	      client.createSchema();
        client.loadData();
	      client.querySchema();
	      client.close();
	   }
	}
