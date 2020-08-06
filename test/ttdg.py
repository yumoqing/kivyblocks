import os
import sys
from functools import partial
from kivyblocks.dg import DataGrid
from kivy.app import App
from kivy.clock import Clock
from appPublic.folderUtils import ProgramPath
from appPublic.jsonConfig import getConfig
from appPublic.timecost import TimeCost
from kivyblocks.blocksapp import appBlocksHack

if __name__ == '__main__':
	pp = ProgramPath()
	workdir = pp
	if len(sys.argv) > 1:
		workdir = sys.argv[1]
	print('ProgramPath=',pp,'workdir=',workdir)

	config = getConfig(workdir,NS={'workdir':workdir,'ProgramPath':pp})


	desc = {
		"paging":True,
		"fields":[
			{
				"freeze":True,
				"width":8,
				"name":"name",
				"label":"Name",
				"datatype":"str"
			},
			{
				"width":50,
				"name":"subject",
				"label":"Subject",
				"datatype":"str"
			},
			{
				"width":10,
				"name":"age",
				"label":"Age",
				"datatype":"int"
			},
			{
				"width":10,
				"name":"gender",
				"label":"Gender",
				"datatype":"int"
			},
			{
				"width":10,
				"name":"grade",
				"label":"Grade",
				"datatype":"str"
			},
			{
				"width":10,
				"name":"since",
				"label":"Since",
				"datatype":"date"
			}
		]
	}
	data = """name1	subject1	34	1	1	1992
name2	subject2	34	1	1	1992
name3	subject3	34	1	1	1992
name4	subject4	34	1	1	1992
name5	subject5	34	1	1	1992
name6	subject6	34	1	1	1992
name7	subject7	34	1	1	1992
name8	subject8	34	1	1	1992
name9	subject9	34	1	1	1992
name10	subject10	34	1	1	1992
name11	subject11	34	1	1	1992
name12	subject12	34	1	1	1992
name13	subject13	34	1	1	1992
name14	subject14	34	1	1	1992
name15	subject15	34	1	1	1992
name16	subject16	34	1	1	1992
name17	subject17	34	1	1	1992
name18	subject18	34	1	1	1992
name19	subject19	34	1	1	1992
name20	subject20	34	1	1	1992
name21	subject21	34	1	1	1992
name22	subject22	34	1	1	1992
name23	subject23	34	1	1	1992
name24	subject24	34	1	1	1992
name25	subject25	34	1	1	1992
name26	subject26	34	1	1	1992
name27	subject27	34	1	1	1992
name28	subject28	34	1	1	1992
name29	subject29	34	1	1	1992
name30	subject30	34	1	1	1992
name31	subject31	34	1	1	1992
name32	subject32	34	1	1	1992
name33	subject33	34	1	1	1992
name34	subject34	34	1	1	1992
name35	subject35	34	1	1	1992
name36	subject36	34	1	1	1992
name37	subject37	34	1	1	1992
name38	subject38	34	1	1	1992
name39	subject39	34	1	1	1992
name40	subject40	34	1	1	1992
name41	subject41	34	1	1	1992
name42	subject42	34	1	1	1992
name43	subject43	34	1	1	1992
name44	subject44	34	1	1	1992
name45	subject45	34	1	1	1992
name46	subject46	34	1	1	1992
name47	subject47	34	1	1	1992
name48	subject48	34	1	1	1992
name49	subject49	34	1	1	1992
name50	subject50	34	1	1	1992
name51	subject51	34	1	1	1992
name52	subject52	34	1	1	1992
name53	subject53	34	1	1	1992
name54	subject54	34	1	1	1992
name55	subject55	34	1	1	1992
name56	subject56	34	1	1	1992
name57	subject57	34	1	1	1992
name58	subject58	34	1	1	1992
name59	subject59	34	1	1	1992
name60	subject60	34	1	1	1992
name61	subject61	34	1	1	1992
name62	subject62	34	1	1	1992
name63	subject63	34	1	1	1992
name64	subject64	34	1	1	1992
name65	subject65	34	1	1	1992
name66	subject66	34	1	1	1992
name67	subject67	34	1	1	1992
name68	subject68	34	1	1	1992
name69	subject69	34	1	1	1992
name70	subject70	34	1	1	1992
name71	subject71	34	1	1	1992
name72	subject72	34	1	1	1992
name73	subject73	34	1	1	1992
name74	subject74	34	1	1	1992
name75	subject75	34	1	1	1992
name76	subject76	34	1	1	1992
name77	subject77	34	1	1	1992
name78	subject78	34	1	1	1992
name79	subject79	34	1	1	1992
name80	subject80	34	1	1	1992
name81	subject81	34	1	1	1992
name82	subject82	34	1	1	1992
name83	subject83	34	1	1	1992
name84	subject84	34	1	1	1992
name85	subject85	34	1	1	1992
name86	subject86	34	1	1	1992
name87	subject87	34	1	1	1992
name88	subject88	34	1	1	1992
name89	subject89	34	1	1	1992
name90	subject90	34	1	1	1992
name91	subject91	34	1	1	1992
name92	subject92	34	1	1	1992
name93	subject93	34	1	1	1992
name94	subject94	34	1	1	1992
name95	subject95	34	1	1	1992
name96	subject96	34	1	1	1992
name97	subject97	34	1	1	1992
name98	subject98	34	1	1	1992
name99	subject99	34	1	1	1992
name100	subject100	34	1	1	1992
name101	subject101	34	1	1	1992
name102	subject102	34	1	1	1992
name103	subject103	34	1	1	1992
name104	subject104	34	1	1	1992
name105	subject105	34	1	1	1992
name106	subject106	34	1	1	1992
name107	subject107	34	1	1	1992
name108	subject108	34	1	1	1992
name109	subject109	34	1	1	1992
name110	subject110	34	1	1	1992
name111	subject111	34	1	1	1992
name112	subject112	34	1	1	1992
name113	subject113	34	1	1	1992
name114	subject114	34	1	1	1992
name115	subject115	34	1	1	1992
name116	subject116	34	1	1	1992
name117	subject117	34	1	1	1992
name118	subject118	34	1	1	1992
name119	subject119	34	1	1	1992
name120	subject120	34	1	1	1992
name121	subject121	34	1	1	1992
name122	subject122	34	1	1	1992
name123	subject123	34	1	1	1992
name124	subject124	34	1	1	1992
name125	subject125	34	1	1	1992
name126	subject126	34	1	1	1992
name127	subject127	34	1	1	1992
name128	subject128	34	1	1	1992
name129	subject129	34	1	1	1992
name130	subject130	34	1	1	1992
name131	subject131	34	1	1	1992
name132	subject132	34	1	1	1992
name133	subject133	34	1	1	1992
name134	subject134	34	1	1	1992
name135	subject135	34	1	1	1992
name136	subject136	34	1	1	1992
name137	subject137	34	1	1	1992
name138	subject138	34	1	1	1992
name139	subject139	34	1	1	1992
name140	subject140	34	1	1	1992
name141	subject141	34	1	1	1992
name142	subject142	34	1	1	1992
name143	subject143	34	1	1	1992
name144	subject144	34	1	1	1992
name145	subject145	34	1	1	1992
name146	subject146	34	1	1	1992
name147	subject147	34	1	1	1992
name148	subject148	34	1	1	1992
name149	subject149	34	1	1	1992
name150	subject150	34	1	1	1992
name151	subject151	34	1	1	1992
name152	subject152	34	1	1	1992
name153	subject153	34	1	1	1992
name154	subject154	34	1	1	1992
name155	subject155	34	1	1	1992
name156	subject156	34	1	1	1992
name157	subject157	34	1	1	1992
name158	subject158	34	1	1	1992
name159	subject159	34	1	1	1992
name160	subject160	34	1	1	1992
name161	subject161	34	1	1	1992
name162	subject162	34	1	1	1992
name163	subject163	34	1	1	1992
name164	subject164	34	1	1	1992
name165	subject165	34	1	1	1992
name166	subject166	34	1	1	1992
name167	subject167	34	1	1	1992
name168	subject168	34	1	1	1992
name169	subject169	34	1	1	1992
name170	subject170	34	1	1	1992
name171	subject171	34	1	1	1992
name172	subject172	34	1	1	1992
name173	subject173	34	1	1	1992
name174	subject174	34	1	1	1992
name175	subject175	34	1	1	1992
name176	subject176	34	1	1	1992
name177	subject177	34	1	1	1992
name178	subject178	34	1	1	1992
name179	subject179	34	1	1	1992
name180	subject180	34	1	1	1992
name181	subject181	34	1	1	1992
name182	subject182	34	1	1	1992
name183	subject183	34	1	1	1992
name184	subject184	34	1	1	1992
name185	subject185	34	1	1	1992
name186	subject186	34	1	1	1992
name187	subject187	34	1	1	1992
name188	subject188	34	1	1	1992
name189	subject189	34	1	1	1992
name190	subject190	34	1	1	1992
name191	subject191	34	1	1	1992
name192	subject192	34	1	1	1992
name193	subject193	34	1	1	1992
name194	subject194	34	1	1	1992
name195	subject195	34	1	1	1992
name196	subject196	34	1	1	1992
name197	subject197	34	1	1	1992
name198	subject198	34	1	1	1992
name199	subject199	34	1	1	1992
name200	subject200	34	1	1	1992
name201	subject201	34	1	1	1992
name202	subject202	34	1	1	1992
name203	subject203	34	1	1	1992
name204	subject204	34	1	1	1992
name205	subject205	34	1	1	1992
name206	subject206	34	1	1	1992
name207	subject207	34	1	1	1992
name208	subject208	34	1	1	1992
name209	subject209	34	1	1	1992
name210	subject210	34	1	1	1992
name211	subject211	34	1	1	1992
name212	subject212	34	1	1	1992
name213	subject213	34	1	1	1992
name214	subject214	34	1	1	1992
name215	subject215	34	1	1	1992
name216	subject216	34	1	1	1992
name217	subject217	34	1	1	1992
name218	subject218	34	1	1	1992
name219	subject219	34	1	1	1992
name220	subject220	34	1	1	1992
name221	subject221	34	1	1	1992
name222	subject222	34	1	1	1992
name223	subject223	34	1	1	1992
name224	subject224	34	1	1	1992
name225	subject225	34	1	1	1992
name226	subject226	34	1	1	1992
name227	subject227	34	1	1	1992
name228	subject228	34	1	1	1992
name229	subject229	34	1	1	1992
name230	subject230	34	1	1	1992
name231	subject231	34	1	1	1992
name232	subject232	34	1	1	1992
name233	subject233	34	1	1	1992
name234	subject234	34	1	1	1992
name235	subject235	34	1	1	1992
name236	subject236	34	1	1	1992
name237	subject237	34	1	1	1992
name238	subject238	34	1	1	1992
name239	subject239	34	1	1	1992
name240	subject240	34	1	1	1992
name241	subject241	34	1	1	1992
name242	subject242	34	1	1	1992
name243	subject243	34	1	1	1992
name244	subject244	34	1	1	1992
name245	subject245	34	1	1	1992
name246	subject246	34	1	1	1992
name247	subject247	34	1	1	1992
name248	subject248	34	1	1	1992
name249	subject249	34	1	1	1992
name250	subject250	34	1	1	1992
name251	subject251	34	1	1	1992
name252	subject252	34	1	1	1992
name253	subject253	34	1	1	1992
name254	subject254	34	1	1	1992
name255	subject255	34	1	1	1992
name256	subject256	34	1	1	1992
name257	subject257	34	1	1	1992
name258	subject258	34	1	1	1992
name259	subject259	34	1	1	1992
name260	subject260	34	1	1	1992
name261	subject261	34	1	1	1992
name262	subject262	34	1	1	1992
name263	subject263	34	1	1	1992
name264	subject264	34	1	1	1992
name265	subject265	34	1	1	1992
name266	subject266	34	1	1	1992
name267	subject267	34	1	1	1992
name268	subject268	34	1	1	1992
name269	subject269	34	1	1	1992
name270	subject270	34	1	1	1992
name271	subject271	34	1	1	1992
name272	subject272	34	1	1	1992
name273	subject273	34	1	1	1992
name274	subject274	34	1	1	1992
name275	subject275	34	1	1	1992
name276	subject276	34	1	1	1992
name277	subject277	34	1	1	1992
name278	subject278	34	1	1	1992
name279	subject279	34	1	1	1992
name280	subject280	34	1	1	1992
name281	subject281	34	1	1	1992
name282	subject282	34	1	1	1992
name283	subject283	34	1	1	1992
name284	subject284	34	1	1	1992
name285	subject285	34	1	1	1992
name286	subject286	34	1	1	1992
name287	subject287	34	1	1	1992
name288	subject288	34	1	1	1992
name289	subject289	34	1	1	1992
name290	subject290	34	1	1	1992
name291	subject291	34	1	1	1992
name292	subject292	34	1	1	1992
name293	subject293	34	1	1	1992"""

	class MyApp(App):
		def build(self):
			with TimeCost('create widget') as tc:
				dg = DataGrid(**desc)
				Clock.schedule_once(self.loadData,1)
				return dg

		def loadData(self,t=None):
			d = []
			for t in data.split('\n'):
				r = self.text2rec(t)
				d.append(r)
			with TimeCost('setData()') as tc:
				self.root.setData(d)
			return 

		def text2rec(self,text):
			d = text.split('\t')
			r = {}
			for i,f in enumerate(desc['fields']):
				r[f['name']] = d[i]
			return r

		def on_close(self,*args,**kwargs):
			return True

	myapp = MyApp()
	appBlocksHack(myapp)
	myapp.run()
	tc = TimeCost('show')
	tc.show()

