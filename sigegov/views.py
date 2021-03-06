import json
from django.core.mail import send_mail
from django.core import serializers
from django.utils.timezone import now as utcnow
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse
import datetime
from datetime import datetime as dt
from django.core.urlresolvers import reverse
from django.template import RequestContext, loader
from sigegov.models import Choice, Question, Donor, Recepient, Hospital, Camp, Link, Post, Story,Notification, User, Publications, UserProfile, Event
from vote.managers import Vote
from sigegov.forms import PublicationsSearchForm, UploadEventForm
from django.contrib.auth.decorators import login_required
from haystack.query import SearchQuerySet
from django.shortcuts import redirect
from django.db.models import Q
import csv
import logging
current_path="/sigegov/home"
emailil="sigegov.gov@gmail.com"
#emailil="akash.wanted@gmail.com"
def home(request):
    	current_path=request.get_full_path()
        flag=0
        context={}
        username = request.user.username
        is_superuser=request.user.is_superuser
        print is_superuser
        if(is_superuser):
                    print "enter admind area"
	            flag=1
	            pending_user_list1=UserProfile.objects.filter(status=0)
		    accepted_user_list1=UserProfile.objects.filter(status=1)
		    pending_user_list=[]
		    accepted_user_list=[]
		    for user in pending_user_list1:
		            if(user.user.username=='admin'):
		                    continue
		            calc=user.user_id
		            userit=User.objects.get(id=calc)
		            pending_user_list.append(userit)
		    for user in accepted_user_list1:
		            if(user.user.username=='admin'):
		                    continue
		            calc=user.user_id
		            userit=User.objects.get(id=calc)
		            accepted_user_list.append(userit)
		    context = {'pending_user_list': pending_user_list, 'accepted_user_list': accepted_user_list, 'flag': flag}
	elif request.user.is_authenticated():#if someone logged in
                user=UserProfile.objects.get(user_id=request.user.id)
		if(user.status==0):
		        flag=2
			return redirect('not_authorized')
		else:
			flag=3
			context={'flag': flag, 'current_path': current_path}
        else:
                flag = 199
                context={'flag': flag}
	return render(request, 'sigegov/index.html',context);
'''

def home(request):
    	current_path=request.get_full_path()
        flag=0
        context={'flag': flag}
        username = request.user.username
        is_superuser=request.user.is_superuser
        if(is_superuser):
            flag=1
	    pending_user_list1=UserProfile.objects.filter(status=0)
	    accepted_user_list1=UserProfile.objects.filter(status=1)
	    pending_user_list=[]
	    accepted_user_list=[]
	    for user in pending_user_list1:
                    if(user.user.username=='admin'):
                        continue
                    calc=user.user_id
                    userit=User.objects.get(id=calc)
                    pending_user_list.append(userit)
		for user in accepted_user_list1:
                    if(user.user.username=='admin'):
                        continue
                    calc=user.user_id
                    userit=User.objects.get(id=calc)
                    accepted_user_list.append(userit)
            	context = {'pending_user_list': pending_user_list, 'accepted_user_list': accepted_user_list, 'flag': flag}
            else:
                user=UserProfile.objects.get(user_id=request.user.id)
		if(user.status==0):
		    	flag=2
			return redirect('not_authorized')
		else:
			flag=3
		context={'flag': flag, 'current_path': current_path}
	return render(request, 'sigegov/index.html',context);
'''
def autocomplete(request):
        if not request.user:
		return redirect('not_authorized')
	user=UserProfile.objects.get(user_id=request.user.id)
	if(user.status==0):
		flag=2
		return redirect('not_authorized')
    	current_path=request.get_full_path()
	search_text = request.GET.get('search_text')
	project_title = request.GET.get('project_title')
	state = request.GET.get('state')
	category = request.GET.get('category')
	department_name = request.GET.get('department_name')
	if project_title or state or category or department_name or search_text:
	#dat = request.GET.get('dat')
	        sqs = SearchQuerySet().autocomplete(project_title_auto=project_title, state_auto=state, category_auto=category, department_name_auto=department_name, text = search_text)
	else:
		#logging.error(search_text)
		sqs = SearchQuerySet()#.autocomplete(text=search_text)
	logging.error(sqs[0].id)
        #sqs1 = SearchQuerySet().autocomplete(department_name_auto=department_name, category_auto= category)
        #sqs1 = SearchQuerySet().autocomplete(project_title_auto=project_title)
        suggestions = [(result.project_title, result.state, result.category, result.department_name, (result.id).split('.')[2]) for result in sqs]
        #suggestions1 = [(result.project_title, result.state) for result in sqs1]

        """sqs = SearchQuerySet().autocomplete(project_title_auto=project_title,
                state_auto=state,
         #       date_auto=dat,
                category_auto=category,
                department_name_auto=department_name)
        suggestions = [(result.project_title, result.state, result.result.category, result.department_name) for result in sqs]"""
        
        """if key == 'title':
	        sqs = SearchQuerySet().autocomplete(project_auto=request.GET.get('q','asdfas'),state_auto='Madhya')
	        suggestions = [result.project_title for result in sqs]
                logging.error(len(suggestions))
        if key == 'state':
                #sqs = SearchQuerySet().models(Publications)
                #sqs.filter(document_id="2013-03")
                #sqs1 = sqs.filter(state_auto = request.GET.get('q','asdf'))
                #sqs2 = sqs.filter(project_auto = 'Gujarat')
                #sqs = sqs1 | sqs2
	        #sqs = SearchQuerySet().autocomplete(state_auto=request.GET.get('q','asdfas'))
	        #sqs = SearchQuerySet().autocomplete(state_auto=request.GET.get('q','asdfas'))
                #for result in sqs:
                #        logging.error(dir(result))
	        suggestions = [(result.project_title,result.state) for result in sqs]
                logging.error(len(suggestions))
        if key == 'category':
	        sqs = SearchQuerySet().autocomplete(category_auto=request.GET.get('q','asdfas'))
	        suggestions = [(result.project_title,result.category) for result in sqs]
        #logging.error(suggestions)"""
	the_data = json.dumps({
	         'results': suggestions
	})
	return HttpResponse(the_data, content_type='application/json')

@login_required
def publications(request,stateID=None):
	user=UserProfile.objects.get(user_id=request.user.id)
	if(user.status==0):
		flag=2
		return redirect('not_authorized')
    	current_path=request.get_full_path()
	form = PublicationsSearchForm(request.GET)
	publications = form.search()
	context = {'publications':publications,'state':stateID, 'current_path': current_path}
	return render(request,'sigegov/publications.html',context)

@login_required
def members(request):
	user=UserProfile.objects.get(user_id=request.user.id)
	if(user.status==0):
		flag=2
		return redirect('not_authorized')
    	current_path=request.get_full_path()
	members = UserProfile.objects.filter(status=1)
	accepted_user_list=[]
	for user in members:
		 calc=user.user_id
	         userit=User.objects.get(id=calc)
	         accepted_user_list.append(userit)
	context = {'members':accepted_user_list, 'current_path': current_path}
	return render(request,'sigegov/members.html',context)

@login_required
def objectives(request):
	user=UserProfile.objects.get(user_id=request.user.id)
	if(user.status==0):
		return redirect('not_authorized')
    	current_path=request.get_full_path()
	context = {'i': 1, 'current_path': current_path}
	return render(request, 'sigegov/objectives.html', context)

@login_required
def executive_committee(request):
	user=UserProfile.objects.get(user_id=request.user.id)
	if(user.status==0):
		return redirect('not_authorized')
    	current_path=request.get_full_path()
	context = {'i': 1, 'current_path': current_path}
	return render(request, 'sigegov/executive_committee.html', context)

@login_required
def create_event(request):
	user=UserProfile.objects.get(user_id=request.user.id)
	if(user.status==0):
		return redirect('not_authorized')
    	current_path=request.get_full_path()
	if request.method=='POST':
		form=UploadEventForm(request.POST, request.FILES)
		if form.is_valid():
			event = form.cleaned_data['event']
			organiser = form.cleaned_data['organiser']
			attachment = form.cleaned_data['attachment']
			#handle_uploaded_file(request.FILES['file'])
			#form.event=request.POST['event']
			#form.organiser=request.POST['organiser']
			#print request.POST
			#form.attachment=request.POST['attachment']
			instance = Event(organiser=organiser,event=event,attachment=attachment)
			instance.save()
			return HttpResponseRedirect('/sigegov/')
	else:
		form=UploadEventForm()
	context = {'form': form, 'current_path': current_path}
	return render(request, 'sigegov/create_event.html',context)

def pdfopen(request, pdf_id=None):
    current_path=request.get_full_path()
    pub = Publications.objects.get(id=pdf_id)
    if pub.attachment:
	    with open(str(pub.attachment), 'rb') as pdf:
		response = HttpResponse(pdf.read(),content_type='application/pdf')
		response['Content-Disposition'] = 'filename=some_file.pdf'
		return response
	    pdf.closed
    context = {'current_path': current_path}
    return render(request, 'sigegov/pdfopen.html',context)

def download(request, file_name=None):
    current_path=request.get_full_path()
    logging.error(file_name)
    with open('./'+file_name, 'rb') as pdf:
	response = HttpResponse(pdf.read(),content_type='application/pdf')
	response['Content-Disposition'] = 'filename=some_file.pdf'
	return response
    pdf.closed
@login_required
def show_event(request):
	user=UserProfile.objects.get(user_id=request.user.id)
	if(user.status==0):
		return redirect('not_authorized')
	current_path=request.get_full_path()
	print current_path
	events = Event.objects.all()
	context = {'events': events, 'current_path': current_path}
	return render(request, 'sigegov/show_events.html',context)

@login_required
def view_publication(request, pubID):
	user=UserProfile.objects.get(user_id=request.user.id)
	if(user.status==0):
		return redirect('not_authorized')
	current_path=request.get_full_path()
	uID = request.user.id
	pub = Publications.objects.get(id=pubID)
	p_count = Vote.objects.filter(Q(object_id=pubID), Q(user_id=uID))
	p_count = len(p_count)
	flag=0
	if(p_count == 1):
		flag=1
	count = Vote.objects.filter(object_id=pubID)
	count = len(count)
	for field in pub._meta.fields:
		print field.name
	context = {'pub': pub, 'flag': flag, 'count': count, 'current_path': current_path, 'pubID': pubID}
	return render(request, 'sigegov/view_publication.html',context)

@login_required
def compare_publications(request, pubId_list):
	user=UserProfile.objects.get(user_id=request.user.id)
	if(user.status==0):
		return redirect('not_authorized')
	current_path=request.get_full_path()
        pubsIds = pubId_list.split(',')
        logging.error(pubsIds)
        pubs = []
        pubs1=[]
        pubs2=[]
        pubs1.append(Publications.objects.get(id=pubsIds[0]))
        pubs2.append(Publications.objects.get(id=pubsIds[1]))
        pubs1=pubs1[0]
        pubs2=pubs2[0]
	context = {'pubs1': pubs1, 'pubs2': pubs2}
	return render(request, 'sigegov/compare_publications.html',context)

@login_required
def process_upvote(request, pubID):
	user=request.user
	pub=Publications.objects.get(pk=pubID)
	pub.votes.up(user)
	return redirect('/sigegov/view_publication/'+str(pubID)+'/')

@login_required
def process_downvote(request, pubID):
	user=request.user
	pub=Publications.objects.get(pk=pubID)
	pub.votes.down(user)
	return redirect('/sigegov/view_publication/'+str(pubID)+'/')


@login_required
def view_request(request,requestID):
	user=UserProfile.objects.get(user_id=request.user.id)
	if(user.status==0):
		return redirect('not_authorized')
	request_list=Recepient.objects.get(id=requestID)
	context={'requestit':request_list}
	return render(request,'blood/view_request.html',context)

@login_required
def view_statewise(request):
	user=UserProfile.objects.get(user_id=request.user.id)
	if(user.status==0):
		return redirect('not_authorized')
	context = {}
	return render(request,'sigegov/view_statewise.html',context)

@login_required
def enter_data(request):
	"""Used for entering the data into the Publications database."""
	with open("text.csv", 'rU') as csvfile:
	   spamreader = csv.reader(csvfile, delimiter=';')	
	   lines = []
     	   for line in spamreader:
         	#line =  line.split(';') 
		#lines.append(line)
		product = Publications()
		product.document_id = line[0]
		product.project_title = line[1]
		product.department_name = line[2]
		product.name_1 = line[3]
		product.designation_1 = line[4]
		product.email_1 = line[5]
		product.address_1 = line[6]
		product.phone_1 = line[7]
		product.fax_1 = line[8]
		product.mobile_1 = line[9]
		product.name_2 = line[10]
		product.designation_2 = line[11]
		product.email_2 = line[12]
		product.address_2 = line[13]
		product.phone_2 = line[14]
		product.fax_2 = line[15]
		product.mobile_2 = line[16]
		product.category = line[17]
		product.nature = line[18]
		product.description = line[19]
		product.date = line[20]
		product.url = line[21]
		product.business_model = line[22]
		product.no_process = line[23]
		product.beneficiary_1 = line[24]
		product.beneficiary_2 = line[25]
		product.beneficiary_3 = line[26]
		product.transaction = line[27]
		product.benefit_1 = line[28]
		product.benefit_2 = line[29]
		product.benefit_3 = line[30]
		product.process_1 = line[31]
		product.process_2 = line[32]
		product.process_3 = line[33]
		product.database = line[34]
		product.operating = line[35]
		product.web_server = line[36]
		product.prime_agency = line[37]
		product.network_arrangement = line[38]
		product.datacenter = line[39]
		product.csc = line[40]
		product.formal_document = line[41]
		product.implementation = line[42]
		product.no_training = line[43]
		product.sector = line[44]
		product.sub_sector = line[45]
		product.state = line[46]
		product.save()  
	context = {'value':lines}
	return render(request,'sigegov/enter.html',context)
	#html = "<html><body>Data Successfully entered.</body>"+spamreader+"</html>"
	#return HttpResponse(html)

@login_required
def view_request_thanks(request,requestID):
	user=UserProfile.objects.get(user_id=request.user.id)
	if(user.status==0):
		return redirect('not_authorized')
	request_list=Recepient.objects.get(id=requestID)
	val=str(request.user)
	val1=str(request.user.email)
	body="Mr "+val+" wants to donate blood to your need.\n\nDetails:\n"
	body+="Name: "+val1+"\nEmail: "+val1+"\n"
	body+="\nKindly contact the user in case of need\n\nRegards,\nBloodConnect\n"
	subject="Regarding Blood Donation at BloodConnect"
	mailit=[]
	mailit.append(request_list.email)
	send_mail(subject, body, emailil,mailit)
	context={'requestit':request_list}
	return render(request,'blood/view_request_thanks.html',context)

def main(request):
	return render(request,'sigegov/index.html')
@login_required
def send_email1(request):
	email=request.user.email
	rst=Recepient.objects.filter(email=email)
	bggroup=rst[0].bggroup
	don=Donor.objects.filter(bggroup=bggroup)
	for i in don:
		to_addr=i.email
		body="You can save many lives"
		subject="Regarding Blood Donation Request"
		mailit=[]
		mailit.append(i.email)
		send_mail(subject, body, email,mailit)
	return render(request,'blood/send_email1.html')

@login_required
def index(request):
    if request.user.is_authenticated():
	user=request.user.username
	email = request.user.email
    	context = {'user': user, 'email': email}
    return render(request, 'sigegov/index.html', context)

@login_required
def donor(request):
	order_list = Donor.objects.all().order_by('name')
	print order_list
	context = {'order_list': order_list}
	return render(request, 'blood/donor.html', context)

@login_required
def share(request):
	user = request.user.username
	new_var=Story.objects.filter(suser__id=request.user.id)
	order_list = Story.objects.all().order_by('tag')
	context = {'order_list': order_list,'user': user, 'new_var':new_var}
	return render(request, 'blood/share.html', context)

@login_required
def view_story(request,story_id):
	order_list = Story.objects.get(id=story_id)
	context = {'order_list': order_list}
	return render(request, 'blood/view_story.html', context)
#	order_list = Story.objects.
@login_required
def not_authorized(request):
	context={'flag': 1}
	return render(request, 'sigegov/not_authorized.html',context)

@login_required
def authorize_user(request, userID):
	user=UserProfile.objects.get(user_id=userID)
	user.status=1
	body="Hi,\n\nYour membership request has been approved by admin. You can now login into the system.\n\nRegards,\nSigeGov Team"
	subject="Regarding Membership Request at Sigegov"
	mailit=[]
	mailit.append(user.user.email)
	user.save()
	send_mail(subject, body, emailil,mailit)

	return redirect('home')
@login_required
def user_details(request, userID):
	user=User.objects.get(id=userID)
	user.save()
	context={'user': user}
	return render(request, 'sigegov/user_details.html',context);
@login_required
def camp_donate(request,campID):
	query = Camp.objects.get(id=campID)
	st = query.sdate+"T00:00:00.000-08:00"#.split("/")
	en = query.edate+"T00:00:00.000-08:00"
	form=Link()
	form.cid=campID
	form.uid=request.user.id
	form.flag=1
	form.guser=request.user
	form.save()
	context = {'st':st,'en':en,'query':query}
	return render(request,'blood/camp_donate.html',context)

@login_required
def todaycamp(request):
	camp_list=Camp.objects.all()
	campit=[]
	flag={}
	for camp in camp_list:
		sdate1=dt.strptime(camp.sdate,'%Y-%m-%d').date()
		edate1=dt.strptime(camp.edate,'%Y-%m-%d').date()
		if(sdate1<=datetime.date.today() and edate1>=datetime.date.today()):
			campit.append(camp)
		ln=Link.objects.filter(cid=camp.id).filter(guser=request.user)
		if len(ln)>0:
		 	flag[camp.id]=1
		else:
		 	flag[camp.id]=0
		#print sdate1,edate1,datetime.date.today()
		#camp_list=Camp.objects.filter(datetime.strptime(sdate,'%Y-%m-%d')<=datetime.date.today()).filter(datetime.strptime(edate,'%Y-%m-%d')>=datetime.date.today())
	email=request.user
	context={'camp_list':campit, 'email':email,'flag':flag}
	return render(request,'blood/todaycamp.html', context)
def faqs(request):
	return render(request, 'blood/faqs.html');
def feedback(request):
	return render(request, 'blood/feedback.html');
def contact(request):
	return render(request, 'blood/contact.html');
def about(request):
	return render(request, 'blood/about.html');

@login_required
def drive(request):
	if request.user.is_authenticated:
		user = request.user.username
	#Either use it as a string or pdf ???
	query = Camp.objects.filter(email=request.user.email)
	context = {'user':user,'q':query}
	return render(request, 'blood/drive.html',context)

@login_required
def drive_list(request,driveID):
	user = request.user.username
	#Either use it as a string or pdf ???
	cdetails = Camp.objects.get(id=int(driveID))
	query = Link.objects.filter(cid=int(driveID))
	corg=cdetails.uid
	corg=User.objects.get(id=corg)
	print query
	dquery = []
	a = []
	b=[]
	ldquery = 0
	emailit=[]
	for i in query:
		#print i.user.get(pk=1)
		a.append(i.guser)
		dquery.append(a)
		a=[]
		#print i.user.objects.all()
		#us=i.user.get(pk=1)
		#us=us.id
		us=User.objects.get(id=i.uid)
	#	print us
	#	queryit=User.objects.get(id=us)
		b.append(us.email)
		emailit.append(b)
		b=[]
	#print json.dumps(dquery)
	context = {'user':user,'q':query,'corg':corg,'cdetails':cdetails,'tdon':len(query),'dquery':json.dumps(dquery),'emailit':json.dumps(emailit)}
	return render(request, 'blood/drive_list.html',context)

@login_required
def calendar(request):
	if request.user.is_authenticated:
		user = request.user.username
	#Query To get the start and end date of camp Assuming one element
	query = Camp.objects.filter(email=request.user.email)
	st=""
	en=""
	if len(query)>0:
		st = query[0].sdate+"T00:00:00.000-08:00"#.split("/")
		en = query[0].edate+"T00:00:00.000-08:00"#.split("/")
	context = {'user':user , 'st':st,'en':en}
	return render(request, 'blood/calendar.html',context)


@login_required
def putstory(request):
	if request.method=='POST':
		form=Story()
		form.tag=request.POST['description']
		form.story=request.POST['bio']
		form.save()
		form.suser.add(request.user)
		return render(request, 'blood/putstory_thanks.html')
	return render(request,'blood/putstory.html')

@login_required
def putstory_thanks(request):
	return render(request, 'blood/putstory_thanks.html')

@login_required
def stry(request):
	order_list = Story.objects.all().order_by('tag')
	context = {'order_list': order_list}
	return render(request, 'blood/stry.html', context)

@login_required
def requestblood_form(request):
	if request.user.is_authenticated:
		user = request.user.username
	query = Recepient.objects.filter(email=request.user.email)
	if len(query)==1:
		query = query[0]
	context = {'user':user,'query':query}
	if request.method=='POST':
		query = Recepient.objects.filter(email=request.user.email)
		if len(query)==1:
			query=query[0]
			query.name=request.POST['name']
			query.address=request.POST['address']
			query.age=request.POST['age']
			query.bggroup=request.POST['bg']
			query.bgunits=request.POST['bunits']
			query.contact=request.POST['contact']
			query.lat1=request.POST['latitude']
			query.long1=request.POST['longitude']
			body="You have saved many lives. Thank You "+query.name+" for your donation.\n"
			body+="You can find list of all interested donors on this map "+"bloodconnect.bluemix.net/blood/donor_list\n"
			body+="\nDetails:\n"
			body+="Name: "+query.name+"\n"+"Blood Group: "+query.bggroup+"\n"+"Blood Units: "+str(query.bgunits)
			body+="\n"+"Contact: "+str(query.contact)+"\nAddress: "+query.address+"\n\nRegards,\nBloodConnect"
			subject="Regarding Blood Donation Request at BloodConnect"
			mailit=[]
			mailit.append(request.user.email)
			send_mail(subject, body, emailil,mailit)
			query.save()
			return HttpResponseRedirect('/blood/donor_list/')
		else:
			form=Recepient()
			form.name=request.POST['name']
			form.address=request.POST['address']
			form.age=request.POST['age']
			form.bggroup=request.POST['bg']
			form.bgunits=request.POST['bunits']
			form.contact=request.POST['contact']
			form.lat1=request.POST['latitude']
			form.long1=request.POST['longitude']
			form.email=request.user.email
			body="You have saved many lives. Thank You "+form.name+" for your donation.\n"
			body+="You can find list of all interested donors on this map "+"bloodconnect.bluemix.net/blood/donor_list\n"
			body+="\nDetails:\n"
			body+="Name: "+form.name+"\n"+"Blood Group: "+form.bggroup+"\n"+"Blood Units: "+str(form.bgunits)
			body+="\n"+"Contact: "+str(form.contact)+"\nAddress: "+form.address+"\n\nRegards,\nBloodConnect"
			subject="Regarding Blood Donation Request at BloodConnect"
			form.save()
			form.user.add(request.user)
			return HttpResponseRedirect('/blood/donor_list')
	return render(request, 'blood/requestblood_form.html',context)

@login_required
def donor_list(request):
	if request.user.is_authenticated:
		user = request.user.username
	query = Recepient.objects.filter(email=request.user.email)
	if(len(query)!=0):
		donor = Donor.objects.filter(bggroup = query[0].bggroup )
	else:
		donor=[]
	if(len(query)!=0):
		rlat = query[0].lat1
		rlong = query[0].long1
		radd = query[0].address
	else:
		rlat=17.3660
		rlong=78.4760
		radd="Hyderabad, Andhra Pradesh, India"
	ddetails = []
	a = []
	b = []
	final = []
	for i in donor:
		a.append(i.name)
		b.append(i.name)
		a.append(i.email)
		b.append(i.email)
		a.append(i.address)
		b.append(i.address)
		a.append(i.contact)
		b.append(i.contact)
		a.append(i.age)
		b.append(i.age)
		a.append(i.bgunits)
		b.append(i.bgunits)
		ddetails.append(b)
		a.append(i.lat1)
		a.append(i.long1)	
		final.append(a)
		a=[]
		b=[]
	context = {'user':user,'details':ddetails,'rlat':rlat,'rlong':rlong,'radd':radd,'final1':json.dumps(final)}
	return render(request, 'blood/donor_list.html',context)	
	
@login_required
def bloodcamp_list(request):
	flagit=0
	if request.user.is_authenticated:
		user = request.user.username
	query = Camp.objects.filter(email=request.user.email)
	if(len(query)==0):
		camp=Camp.objects.all()
		flagit=1
		rlat=17.385044
		rlong=78.486671
		radd = ""

	camp = Camp.objects.all()
	if(flagit==0):
		rlat = query[0].lat1
		rlong = query[0].long1
		radd = query[0].address
	ddetails = []
	a = []
	b = []
	final = []
	for i in camp:
		a.append(i.name)
		b.append(i.name)
		a.append(i.email)
		b.append(i.email)
		a.append(i.address)
		b.append(i.address)
		a.append(i.contact)
		b.append(i.contact)
		ddetails.append(b)
		a.append(i.lat1)
		a.append(i.long1)	
		final.append(a)
		a=[]
		b=[]
	context = {'user':user,'details':ddetails,'rlat':rlat,'rlong':rlong,'radd':radd,'final1':json.dumps(final)}
	return render(request, 'blood/bloodcamp_list.html',context)

def requestblood_thanks(request):
	return render(request,'blood/requestblood_thanks.html')

def donateblood_thanks(request):
	return render(request,'blood/donateblood_thanks.html')

@login_required
def bloodcamp(request):
	query=Camp.objects.all()
	if(query):
		flagit=0
	else:
		flagit=1
	context={'flagit':flagit}
	return render(request,'blood/bloodcamp.html',context)

def camps_detail(request):
	tot_list=Camp.objects.all()
	selected_camps=Link.objects.filter(guser=request.user)
	going_list=[]
	camp_list=[]
	going=[]
	for i in selected_camps:
		going.append(int(i.cid))
		going_list.append(Camp.objects.get(id=i.cid))
	for i in tot_list:
		if i.id not in going:
			camp_list.append(i)
	email=request.user
	context={'camp_list':camp_list, 'email':email ,'going_list':going_list,'going':going}
	return render(request,'blood/camps_detail.html', context)
@login_required
def send_email_sigegov(request,page_path):
	if request.user.is_authenticated:
		user=request.user.username
	if request.method == 'POST':
		email=[]
		email.append(request.POST['email'])
		message=request.POST['message']
		subject='Sigegov query from '+request.POST['email']
		send_mail(subject, message, emailil, email)
	return redirect(page_path)
@login_required
def bloodcamp_form(request):
	if request.user.is_authenticated:
		user = request.user.username
	if request.method=='POST':
		form=Camp()
		form.name=request.POST['name']
		form.address=request.POST['address']
		form.contact=request.POST['contact']
		form.lat1=request.POST['latitude']
		form.long1=request.POST['longitude']
		valit= datetime.date.today()
		form.cdate=valit
		#print request.POST['sdate']
		form.sdate=request.POST['sdate']
		form.edate=request.POST['edate']
		form.email=request.user.email
		form.uid=request.user.id
		form.save()
		return HttpResponseRedirect('/blood/bloodcamp_list')
	context = {'user':user}
	return render(request, 'blood/bloodcamp_form.html',context)

def bloodcamp_form_thanks(request):
	return render(request,'blood/bloodcamp_form_thanks.html');

def camp_post(request,campID):
	camplist=Camp.objects.get(id=campID)
	uid=camplist.uid
	userit=User.objects.get(id=uid)
	postit=Post.objects.filter(campid=campID)
	ait=[]
	for post in postit:
		valit=post.uid
		value=User.objects.get(id=valit)
		print value
		ait.append(value)
	print ait
	context={'campID':campID, 'camplist':camplist, 'postit':postit, 'userit':userit, 'lit':zip(postit,ait)}
	return render(request,'blood/camp_post.html',context)

def store_camp_post(request,campID):
	if request.method=='POST':
		form=Post()
		form.comment=request.POST['comment']
		form.campid=campID
		form.uid=request.user.id
		form.save()
	return HttpResponseRedirect('/blood/camp_post/'+(campID)+'/')
#return render(request,'blood/camp_post.html/{{campID}}')

@login_required
def donate_blood(request):
	if request.user.is_authenticated:
		user = request.user.username
	query = Donor.objects.filter(email=request.user.email)
	if len(query)==1:
		query = query[0]
	context = {'user':user,'query':query}
	if request.method=='POST':
		query = Donor.objects.filter(email=request.user.email)
		if len(query)==1:
			query=query[0]
			query.name=request.POST['name']
			query.address=request.POST['address']
			query.age=request.POST['age']
			query.bggroup=request.POST['bg']
			query.bgunits=request.POST['bunits']
			query.contact=request.POST['contact']
			query.lat1=request.POST['latitude']
			query.long1=request.POST['longitude']
			body="You have saved many lives. Thank You "+query.name+" for your donation.\n\n"+"Details:\n"
			body+="Name: "+query.name+"\n"+"Blood Group: "+query.bggroup+"\n"+"Blood Units: "+str(query.bgunits)
			body+="\n"+"Contact: "+str(query.contact)+"\nAddress: "+query.address+"\n\nRegards,\nBloodConnect"
			subject="Regarding Blood Donation at BloodConnect"
			mailit=[]
			mailit.append(request.user.email)
			send_mail(subject, body, emailil,mailit)
			query.save()
		else:
			form=Donor()
			form.name=request.POST['name']
			form.address=request.POST['address']
			form.age=request.POST['age']
			form.bggroup=request.POST['bg']
			form.bgunits=request.POST['bunits']
			form.contact=request.POST['contact']
			form.lat1=request.POST['latitude']
			form.long1=request.POST['longitude']
			form.email=request.user.email
			body="You have saved many lives. Thank You "+form.name+" for your donation.\n\n"+"Details:\n"
			body+="Name: "+form.name+"\n"+"Blood Group: "+form.bggroup+"\n"+"Blood Units: "+str(form.bgunits)
			body+="\n"+"Contact: "+str(form.contact)+"\nAddress: "+form.address+"\n\nRegards,\nBloodConnect"
			subject="Regarding Blood Donation at BloodConnect"
			mailit=[]
			mailit.append(form.email)
			send_mail(subject, body, emailil,mailit)
			form.save()
			form.user.add(request.user)
		return render(request, 'blood/donateblood_thanks.html')
	return render(request, 'blood/donate_blood.html',context)

def faqs(request):
	return render(request, 'blood/faqs.html');
def recepient(request):
	order_list = Recepient.objects.all().order_by('name')
	context = {'order_list:': order_list}
	return render(request, 'blood/recepient.html', context)

def hospital(request):
	order_list = Hospital.objects.all().order_by('name')
	context = {'order_list': order_list}
	return render(request, 'blood/hospital.html', context)

def camp(request):
	order_list = Camp.objects.all().order_by('name')
	context = {'order_list': order_list}
	return render(request, 'blood/camp.html', context)

def link(request):
	order_list = Link.objects.all().order_by('cid')
	context = {'order_list': order_list}
	return render(request, 'blood/link.html', context)

def post(request):
	order_list = Post.objects.all().order_by('user')
	context = {'order_list': order_list}

def story(request):
	order_list = Story.objects.all().order_by('user')
	context = {'order_list': order_list}

def Notification(request):
	order_list = Notification.objects.all().order_by('did')
	context = {'order_list': order_list}

def detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'blood/detail.html', {'question': question})

def results(request, question_id):
    response = "You're looking at the results of question %s."
    return HttpResponse(response % question_id)

def vote(request, question_id):
    return HttpResponse("You're voting on question %s." % question_id)

def vote(request, question_id):
    p = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = p.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'polls/detail.html', {
            'question': p,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('polls:results', args=(p.id,)))
