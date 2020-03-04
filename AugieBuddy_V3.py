import heapq


def shortestPath(graph, start, end):
    queue,seen = [(0, start, [])], set()
    while True:
        (cost, v, path) = heapq.heappop(queue)
        if v not in seen:
            path = path + [v]
            seen.add(v)
            if v == end:
                return cost, path
            for (next, c) in graph[v].items():
                heapq.heappush(queue, (cost + c, next, path))
			
graph ={    '1': {'4': 60, '6': 115}, # Solberg
            '2': {'4': 51, '3': 92},  # Bergsaker
            '3': {'2': 92, '5': 59},  # Froiland
            '4': {'1': 60, '2': 51, '5': 60, '6': 77}, # Intersection (Solberg/Bergsaker)
            '5': {'3': 59, '4': 60, '7': 68},         # Madsen
            '6': {'1': 115, '4': 77, '7': 57, '10': 70}, # Humanities
            '7': {'5': 68, '6': 57, '8': 68, '10': 66}, # Intersection (With chapel)
            '8': {'7': 68, '9': 103}, # Fancy bubble building with library/Madsen
            '9': {'8': 103, '10': 82}, # Library 
            '10': {'6': 70, '7': 66, '9': 82}} # The Commons

graph_to_names = { '1': 'Solberg',
                   '2': 'Bergsaker',
                   '3': 'Froiland',
                   '4': 'Intersection 1',
                   '5': 'Madsen Center',
                   '6': 'Humanities',
                   '7': 'Intersection with Chapel',
                   '8': 'Western Studies',
                   '9': 'Library',
                   '10': 'The Commons', }

#startLoc = input("What is your starting location?\n1. Solberg\n2. Bergsaker\n3. Froiland\n4. Intersection 1\
#\n5. Madsen Center\n6. Humanities\n7. Intersection with Chapel\n8. Western Studies\n9. Library\n10. The Commons\n\nEnter the number of your location: ")
#startLoc = startLoc.replace(" ","")

#endLoc = input("\nWhat is your final destination?\n1. Solberg\n2. Bergsaker\n3. Froiland\n4. Intersection 1\
#\n5. Madsen Center\n6. Humanities\n7. Intersection with Chapel\n8. Western Studies\n9. Library\n10. The Commons\n\nEnter the number of your location: ")
#endLoc = endLoc.replace(" ","")

def main(startLoc, endLoc):
    cost, path = shortestPath(graph, startLoc, endLoc)

    m, s = divmod(cost, 60) # This converts the time number entered in the dictionary to minutes and seconds.
    print("\nFastest route from",startLoc,"to",endLoc,"is:",m,"minutes",s,"seconds.\n")# path)
    visited = 0
    for i in path:
        path1 = graph_to_names[i]
        visited = visited + 1
        print(visited,"->",path1)
    # Based on http://code.activestate.com/recipes/119466
