package edu.hu.cassandra;


	import com.datastax.driver.core.Cluster;
	import com.datastax.driver.core.Host;
	import com.datastax.driver.core.Metadata;
	import com.datastax.driver.core.Session;
	import com.datastax.driver.core.ResultSet;
	import com.datastax.driver.core.Row;
	import com.datastax.driver.core.PreparedStatement;
	import com.datastax.driver.core.BoundStatement;
	
	import java.util.HashSet;
	import java.util.Set;
	
	public class P04_PreparedClient {
	   private Cluster cluster;
	   private Session session;
	   public static final String p04 = "p04";

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
		   session.execute("CREATE KEYSPACE " + p04 + " WITH replication " + 
				      "= {'class':'SimpleStrategy', 'replication_factor':1};");
		   session.execute(
			   	"CREATE TABLE " + p04 + ".person (" +
			   			"person_id int PRIMARY KEY," +
			   			"fname text," +
			   			"lname text," +
			   			"city text," +
			   			"cell_phone set<text>);");

	   }

	   public void loadData() {
		   String insertPrefix = "INSERT INTO " + p04 + ".person " + 
			   		"(person_id, fname, lname, city, cell_phone) VALUES";	
		   
		   PreparedStatement statement = session.prepare(
				   insertPrefix + "(?,?,?,?,?);"
				   );
		   BoundStatement boundStatement = new BoundStatement(statement);
		   
		   Set<String> cells = new HashSet<String>();
		   cells.add("+44 20 7925 0918");
		   session.execute(boundStatement.bind(
				   1, "Winston", "Churchill", "London", cells				   
				   ));
		   
		   cells.clear();
		   cells.add("212-504-4115");
		   cells.add("202-456-1111");
		   cells.add("518-474-8390");
		   session.execute(boundStatement.bind(
				   	2, "Franklin", "Roosevelt", "Hyde Park", cells
				   ));
		   
		   cells.clear();
		   cells.add("+7 495 697-03-49");
		   session.execute(boundStatement.bind(
				   	3, "Joseph", "Stalin", "Moscow", cells
				   ));
		   
	   }
	   public void querySchema(){
		   ResultSet results = session.execute(
				   "SELECT fname, lname, city, cell_phone FROM " + p04 + ".person ");
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
		   
		   P04_PreparedClient client = new P04_PreparedClient();
	      client.connect("127.0.0.1");
	      client.createSchema();
          client.loadData();
	      client.querySchema();
	      client.close();
	   }
	}
