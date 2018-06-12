from py2neo import Graph, Path
graph = Graph()

#a.	Add movie = "John Wick"
#b.	Add directors by Chad Stahelski, David Leitch
#c.	Add actors William Dafoe and Michael Nyquist
#d.	Add DIRECTED_BY and ACTS_IN relationships for all
#   - include role property on ACTS_IN

wick = graph.cypher.execute('CREATE (m:Movie {title: {title}, year: {year}}) RETURN m', 
                            title='John Wick', 
                            year = '2014-10-24')[0][0]

tx2 = graph.cypher.begin()
for actor_name in ['William Dafoe','Michael Nyquist']:
    tx2.append('CREATE (a:Actor {name: {name}}) RETURN a', name=actor_name)
will, mike = [result.one for result in tx2.commit()]

will_path = Path(will, ('ACTS_IN', {'role': 'Marcus'}), wick)
graph.create(will_path)

mike_path = Path(mike, ('ACTS_IN', {'role': 'Viggo Tarasov'}), wick)
graph.create(mike_path)

tx3 = graph.cypher.begin()
for director_name in ['Chad Stahelski', 'David Leitch']:
    tx3.append('CREATE (d:Director {name: {name}}) RETURN d', name=director_name)
chad, david = [result.one for result in tx3.commit()]

chad_path = Path(chad, "DIRECTED", wick)
graph.create(chad_path)

david_path = Path(david, "DIRECTED", wick)
graph.create(david_path)
#concise but less readable, don't need to worry about properties on the DIRECTED relationship
#[graph.create(Path(result.one, 'DIRECTED_BY', wick)) for result in tx3.commit()]

tx4 = graph.cypher.begin()
tx4.append('MERGE (a:Actor { name:"Keanu Reeves" })')
tx4.append('MATCH (a:Actor { name:"Keanu Reeves" }) RETURN a')
keanu = tx4.commit()[1].one
keanu_path = Path(keanu, ("ACTS_IN", {'role': 'John Wick'}), wick)
graph.create(keanu_path)

#John Wick: Chapter Two
