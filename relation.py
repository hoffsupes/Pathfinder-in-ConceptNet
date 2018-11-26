import os
import requests
import json
import pdb
import sys

### Usage python relation.py item1 item2 searchtype
### searchtype = {approx,full}
### approx = if any simple isA match is found, even in terms of the labels of the categories, it is a match
### full = a stricter search
### Edge case, when trying something that is not food
### python relation.py bowl food approx
### Result: 
### ['bowl','food']
### But bowl is not a kind of food!
### Let's try again
### python relation.py bowl food full
### Result:
### There was no link to the final node for  bowl
### ['bowl', 'food_vessel', 'kitchenware', 'housewares', 'goods', 'generic_artifact', 'cultural_thing']

def isa_query_creator(node,mode):
	if(mode):
		query = 'http://api.conceptnet.io/query?node=/c/en/'+ node +'&rel=/r/IsA'
	else:
		query = 'http://api.conceptnet.io/query?node='+ node +'&rel=/r/IsA'
	return query;

def rel_query_creator(start,end,mode):
	if(mode):
		query = 'http://api.conceptnet.io/relatedness?node1=/c/en/'+ start + '&node2=/c/en/' + end;
	else:
		query = 'http://api.conceptnet.io/relatedness?node1='+ start + '&node2=' + end;		
	return query;

def get_next_node(start,end,mode):
	rel_list = [];
	ter_list = [];
	t_list = []; # for possible future use
	obj = requests.get(isa_query_creator(start,1)).json();

	for i in range(0,len(obj['edges'])):
		if 'IsA' in obj['edges'][i]['rel']['label']:
			ter_list.append(obj['edges'][i]['end']['term']);
			t_list.append(obj['edges'][i]['end']['term'][6:len(obj['edges'][i]['end']['term'])]);
			rel_list.append(requests.get(rel_query_creator(obj['edges'][i]['end']['term'][6:len(obj['edges'][i]['end']['term'])],end,1)).json()['value']);
	
	t_new = [i for i,m in enumerate(t_list) if m == start ];		## delete any self references
	t_new.sort(reverse=True);
	for i in t_new:
		del(t_list[i]);
		del(ter_list[i]);
		del(rel_list[i]);
	
	if(rel_list == []):
		return 'null','null','FX';
	
	newi = rel_list.index(max(rel_list));
	if mode == 'approx':
		if([i for i in t_list if end in i] != []):
			return end,'/c/en/'+end,'EX';
	#print(t_list[newi])
	return t_list[newi],ter_list[newi],rel_list[newi];

def get_full_list(start,end):
	trav_list = [];
	oldstart = start;
	trav_list.append(start);
	mode = 0;
	while(1):
		name,fullname,relness = get_next_node(start,end,h[3]);
		if (type(relness) == type('string value')):
			if(relness == 'FX'):
				print('There was no link to the final node for ',oldstart);
				mode = 1;
				break;
		if(name.lower() == trav_list[len(trav_list) - 1].lower()):
			print('There was no link to the final node for ',oldstart);
			mode = 1;
			break;
		if(name.lower() == end.lower()):
			trav_list.append(end);
			break;
		trav_list.append(name);
		start = name;
	return trav_list,mode;
h = sys.argv;
li,mo = get_full_list(h[1],h[2]);
print(li);
# requests.get('http://api.conceptnet.io/relatedness?node1=/c/en/tea&node2=/c/en/one_variety_of_tea').json(); # related nodes

