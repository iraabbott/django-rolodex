from django.test import TestCase
from django.test import Client
from django.urls import reverse
from rolodex.models import *
from django_webtest import WebTest
from rolodex.views import *
import json

client = Client()
client.defaults['HTTP_WEBTEST_USER'] = 'webtest'


class RolodexModelsTestCase(TestCase):

	print("Starting models tests...")

	fixtures = ['rolodex_models_testdata.json']

	def setUp(self):
		from rolodex import views as rolodex_views
		rolodex_views.EMPLOYMENT = P2Org_Type.objects.get(relationship_type='employment')
		self.o1 = Org.objects.get(slug="acme-corp")
		self.p1 = Person.objects.get(slug="john-doe")
		self.o2 = Org.objects.get(slug="ajax-corp")
		self.p2 = Person.objects.get(slug="jane-doe")

	def test_getter_methods(self):
		self.assertEqual(list(self.p1.get_relations()['orgs']), [self.o1])
		self.assertEqual(list(self.p1.get_employer()), [self.o1])
		self.assertEqual(list(self.o1.get_employees()), [self.p1])
		self.assertEqual(list(self.o1.get_employees_by_role('boss')), [self.p1])
		self.assertEqual(self.o1.get_relations_by_type('employment')['people'], [{'type': 'employment', 'relation': self.p1}])
		self.assertEqual(self.o1.get_relations_with_type()['people'], [{'type': 'employment', 'relation': self.p1}])
		self.assertEqual(self.p1.nx_graph().has_node(self.o1), True)
		print(" >> Passed getter methods")

	def test_create_relationships(self):
		self.p1.add_p2p(self.p2)
		self.assertEqual(list(self.p1.get_relations()['people']), [self.p2])

		self.o1.add_org2org(self.o2, **{'hierarchy': 'parent'})
		self.assertEqual(Org2Org.objects.get(from_ent=self.o2, to_ent=self.o1).hierarchy, 'child')

		self.o1.add_org2p(self.p2)
		self.assertEqual(list(self.p2.get_relations()['orgs']), [self.o1])
		print(" >> Passed relationship create methods")

	def test_delete_relationships(self):
		self.p1.remove_p2p(self.p2)
		self.assertEqual(list(self.p2.get_relations_with_type()['people']), [])

		self.o1.remove_org2org(self.o2)
		self.assertEqual(list(self.o2.get_relations()['orgs']), [])

		self.o1.remove_org2p(self.p2)
		self.assertEqual(list(self.p2.get_relations()['orgs']), [])
		print(" >> Passed relationship delete methods")


'''
This test is not passing right now. See Org2Org model save method.
'''
# def test_hierarchy_recursion(self):
# 	self.o1.add_org2org(self.o2)
# 	relation = Org2Org.objects.get(from_ent=self.o1,to_ent=self.o2)
# 	relation.hierarchy = 'parent'
# 	relation.save()
# 	self.assertEqual(Org2Org.objects.get(from_ent=self.o2,to_ent=self.o1).hierarchy,'child')
# 	print(" >> Passed hierarchy recursion")


class RolodexViewsTestCase(WebTest):

	print("Starting views tests...")

	fixtures = ['rolodex_views_testdata.json']

	def setUp(self):
		self.app.extra_environ['HTTP_WEBTEST_USER'] = 'webtest'
		from rolodex import views as rolodex_views
		rolodex_views.EMPLOYMENT = P2Org_Type.objects.get(relationship_type='employment')
		self.o1 = Org.objects.get(slug="acme-corp")
		self.p1 = Person.objects.get(slug="john-doe")
		self.o2 = Org.objects.get(slug="ajax-corp")
		self.p2 = Person.objects.get(slug="jane-doe")

	def test_home(self):
		response = client.get(reverse('rolodex_home'))
		self.assertEqual(response.status_code, 200)
		print(" >> Passed home")

	def test_search(self):
		response = client.get(reverse('rolodex_org', args=[self.o1.slug]))
		self.assertContains(response, self.o1.orgName, status_code=200)
		response = client.get(reverse('rolodex_person', args=[self.p1.slug]))
		self.assertContains(response, self.p1.lastName, status_code=200)
		print(" >> Passed entity pages")

	def test_create_edit(self):
		'''
		Add a person with a bad email address. Fix the email and check for successful resubmit.
		'''
		form = self.app.get(reverse('rolodex_new_person', args=[self.o2.slug])).form
		form['lastName'] = 'Rabbit'
		form['firstName'] = 'Roger'
		form['person_contact-0-contact'] = 'nobugsbunny'
		form['person_contact-0-type'] = 'email'
		print(form['lastName'].value)
		response = form.submit()
		self.assertContains(response, 'Enter a valid email address.')
		form = response.form
		form['person_contact-0-contact'] = 'nobugs@gmail.com'
		response = form.submit()
		self.assertEqual(response.context['success'], True)
		'''
		Edit Person
		'''
		form = self.app.get(reverse('rolodex_edit_person', args=[self.p2.slug])).form
		form['lastName'] = 'Doe, Jr.'
		form['position'] = 'Scientist'
		response = form.submit().follow()
		self.assertContains(response, 'Doe, Jr.', status_code=200)
		'''
		Edit Org
		'''
		form = self.app.get(reverse('rolodex_edit_org', args=[self.o2.slug])).form
		form['orgName'] = 'AJAX, Inc.'
		response = form.submit().follow()
		self.assertContains(response, 'AJAX, Inc.', status_code=200)
		'''
		Edit Contact
		'''
		form = self.app.get(reverse('rolodex_edit_person', args=['roger-rabbit'])).form
		form['person_contact-0-contact'] = 'theRealRoger@gmail.com'
		response = form.submit().follow()
		self.assertContains(response, 'theRealRoger@gmail.com')
		# Delete the contact
		form = self.app.get(reverse('rolodex_edit_person', args=['roger-rabbit'])).form
		form['person_contact-0-DELETE'] = True
		response = form.submit().follow()
		self.assertNotContains(response, 'nobugs@gmail.com', status_code=200)
		print(" >> Passed entity create and edit pages")

	def test_remote_search(self):
		'''
		SELECT SEARCH FUNCTIONS

		entity_remote_search
		'''
		get_url = "%s?q=%s" % (reverse(entity_remote_search), 'ACME')
		response = client.get(get_url)
		expected_dict = [
			{
				'url': reverse(search_org, args=[self.o1.slug]),
				'name': self.o1.orgName
			}
		]
		self.assertContains(response, json.dumps(expected_dict), status_code=200)
		'''
		person_remote_search
		'''
		get_url = "%s?q=%s" % (reverse(person_remote_search), 'John')
		response = client.get(get_url)
		expected_dict = [
			{
				'pk': self.p1.pk,
				'p-url': reverse(search_person, args=[self.p1.slug]),
				'name': "%s, %s" % (self.p1.lastName, self.p1.firstName),
				'role': 'boss',
				'org': 'ACME, Corp.'
			}
		]
		self.assertContains(response, json.dumps(expected_dict), status_code=200)
		'''
		org_remote_search
		'''
		get_url = "%s?q=%s" % (reverse(org_remote_search), 'Acme')
		response = client.get(get_url)
		expected_dict = [
			{
				'pk': self.o1.pk,
				'org-url': reverse(search_org, args=[self.o1.slug]),
				'new-p-url': reverse(new_person, args=[self.o1.slug]),
				'name': "ACME, Corp.",
			}
		]
		self.assertContains(response, json.dumps(expected_dict), status_code=200)
		print(" >> Passed remote search test")

	def test_relation_create(self):
		'''
		Correspond to the new_org_relation & new_person_relation views.

		Org2Org
		'''
		form = self.app.get(reverse('rolodex_new_org_relation', args=[self.o1.slug])).forms[0]
		form['to_ent'].force_value(self.o2.pk)  # Force value for AJAX field
		form['hierarchy'] = 'parent'
		response = form.submit()
		self.assertEqual(response.status_code, 200)
		self.assertEqual(Org2Org.objects.get(from_ent=self.o2, to_ent=self.o1).hierarchy, 'child')
		'''
		Check no duplicate relationships
		'''
		form = self.app.get(reverse('rolodex_new_org_relation', args=[self.o1.slug])).forms[0]
		form['to_ent'].force_value(self.o2.pk)
		response = form.submit()
		self.assertContains(response, 'That relationship already exists.')

		'''
		Org2P
		'''
		form = self.app.get(reverse('rolodex_new_org_relation', args=[self.o2.slug])).forms[1]
		form['to_ent'].force_value(self.p2.pk)
		response = form.submit()
		self.assertEqual(response.context['saved'], True)
		'''
		P2P
		'''
		form = self.app.get(reverse('rolodex_new_person_relation', args=[self.p2.slug])).forms[1]
		form['to_ent'].force_value(self.p1.pk)
		response = form.submit()
		self.assertEqual(response.context['saved'], True)
		'''
		P2Org
		'''
		form = self.app.get(reverse('rolodex_new_person_relation', args=[self.p2.slug])).forms[0]
		form['to_ent'].force_value(self.o1.pk)
		response = form.submit()
		self.assertEqual(response.context['saved'], True)

		print(" >> Passed relationship create page")

	def test_delete(self):
		response = client.post(reverse('rolodex_delete_person', args=[self.p2.slug]))
		self.assertEqual(response.status_code, 302)
		response = client.post(reverse('rolodex_delete_org', args=[self.o2.slug]))
		self.assertEqual(response.status_code, 302)
		print(" >> Passed delete page")


'''
Fixtures...
'''
# from rolodex.models import *
# RELATION, get = P2Org_Type.objects.get_or_create(relationship_type='employment')
# ROLE = PersonRole.objects.create(role="boss")
# CONTACT_ROLE = OrgContactRole.objects.create(role="front desk")
# o1 = Org.objects.create(orgName="ACME, Corp.")
# p1 = Person.objects.create(firstName='John', lastName='Doe', role=ROLE)
# p1.add_p2org(o1,**{'relation':RELATION})
# Org.objects.create(orgName="AJAX, Corp.")
# Person.objects.create(firstName='Jane', lastName='Doe')

# python manage.py dumpdata rolodex --format=json --indent=4 > testproject/fixtures/rolodex_models_testdata.json
# python manage.py dumpdata rolodex --format=json --indent=4 > testproject/fixtures/rolodex_views_testdata.json


class OrgHierarchyAPITestCase(TestCase):

	def setUp(self):
		self.parent = Org.objects.create(orgName='Parent Org')
		self.child = Org.objects.create(orgName='Child Org')
		self.grandchild = Org.objects.create(orgName='Grandchild Org')
		self.relation_type = Org2Org_Type.objects.create(relationship_type='ownership')
		self.parent.add_org2org(self.child, relation=self.relation_type, hierarchy='parent')
		self.child.add_org2org(self.grandchild, relation=self.relation_type, hierarchy='parent')
		self.employment = P2Org_Type.objects.create(relationship_type='employment')
		self.employee = Person.objects.create(firstName='Ella', lastName='Employee')
		self.child.add_org2p(self.employee, relation=self.employment)

	def test_tree_default_depth(self):
		url = reverse('rolodex_org_hierarchy', args=[self.parent.slug])
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)
		payload = response.json()
		self.assertEqual(payload['slug'], self.parent.slug)
		self.assertEqual(len(payload['children']), 1)
		self.assertEqual(payload['children'][0]['slug'], self.child.slug)
		self.assertEqual(payload['children'][0]['children'][0]['slug'], self.grandchild.slug)

	def test_tree_respects_depth(self):
		url = f"{reverse('rolodex_org_hierarchy', args=[self.parent.slug])}?depth=1"
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)
		payload = response.json()
		self.assertEqual(len(payload['children']), 1)
		self.assertEqual(payload['children'][0]['children'], [])

	def test_tree_includes_members_and_parents(self):
		child_url = f"{reverse('rolodex_org_hierarchy', args=[self.child.slug])}?include_members=true&include_parents=true&depth=0"
		response = self.client.get(child_url)
		self.assertEqual(response.status_code, 200)
		payload = response.json()
		self.assertEqual(payload['member_count'], 1)
		self.assertEqual(payload['members'][0]['slug'], self.employee.slug)
		self.assertEqual(payload['parents'][0]['slug'], self.parent.slug)
