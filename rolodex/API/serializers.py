from rest_framework import serializers

from rolodex.models import Person, Org, Contact, PersonRole, OrgContactRole, P2P, Org2Org, P2Org, Org2P, P2P_Type, Org2Org_Type, P2Org_Type
from django.contrib.auth.models import User


class RoleSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = PersonRole
		fields = ('role', 'description')


class ContactRoleSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = OrgContactRole
		fields = ('role', 'description')


class P2P_TypeSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = P2P_Type
		fields = ('relationship_type',)


class Org2Org_TypeSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = Org2Org_Type
		fields = ('relationship_type',)


class P2Org_TypeSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = P2Org_Type
		fields = ('relationship_type',)


class PersonSerializer(serializers.HyperlinkedModelSerializer):
	# people = serializers.HyperlinkedRelatedField(many=True, read_only=True,view_name='p_relations')
	# orgs = serializers.HyperlinkedRelatedField(many=True, read_only=True,view_name='org_relations')
	# person_role = serializers.HyperlinkedRelatedField(many=True, read_only=False,view_name='role',queryset=PersonRole.objects.all())
	class Meta:
		model = Person
		fields = ('id', 'slug', 'firstName', 'lastName', 'position', 'department', 'gender', 'role', 'person_contact', 'org_relations', 'p_relations')


class OrgSerializer(serializers.HyperlinkedModelSerializer):
	# people = serializers.HyperlinkedRelatedField(many=True, read_only=True,view_name='person-relations')
	# orgs = serializers.HyperlinkedRelatedField(many=True, read_only=True,view_name='org-relations')
	class Meta:
		model = Org
		fields = ('id', 'slug', 'orgName', 'org_relations', 'p_relations', 'org_contact')


class ContactSerializer(serializers.HyperlinkedModelSerializer):
	# person_contact = serializers.HyperlinkedRelatedField( read_only=False,view_name='person',queryset=Person.objects.all())
	# org_contact = serializers.HyperlinkedRelatedField( read_only=False,view_name='org',queryset=Org.objects.all())
	class Meta:
		model = Contact
		fields = ('id', 'person', 'org', 'type', 'contact', 'role', 'notes')


class P2PSerializer(serializers.HyperlinkedModelSerializer):
	# p_from_p = serializers.HyperlinkedRelatedField( read_only=False,view_name='from_person',queryset=Person.objects.all())
	# p_to_p = serializers.HyperlinkedRelatedField( read_only=False,view_name='to_person',queryset=Person.objects.all())
	# p2p_relation = serializers.HyperlinkedRelatedField( read_only=False,view_name='relationship_type',queryset=P2P_Type.objects.all())
	class Meta:
		model = P2P
		fields = ('id', 'from_ent', 'to_ent', 'relation', 'from_date', 'to_date', 'description')


class Org2OrgSerializer(serializers.HyperlinkedModelSerializer):
	# org_from_org = serializers.HyperlinkedRelatedField( read_only=False,view_name='from_org',queryset=Org.objects.all())
	# org_to_org = serializers.HyperlinkedRelatedField( read_only=False,view_name='to_org',queryset=Org.objects.all())
	# org2org_relation = serializers.HyperlinkedRelatedField( read_only=False,view_name='relationship_type',queryset=Org2Org_Type.objects.all())
	class Meta:
		model = Org2Org
		fields = ('id', 'from_ent', 'to_ent', 'relation', 'from_date', 'to_date', 'description')


class P2OrgSerializer(serializers.HyperlinkedModelSerializer):
	# org_from_p = serializers.HyperlinkedRelatedField( read_only=False,view_name='from_person',queryset=Person.objects.all())
	# p_to_org = serializers.HyperlinkedRelatedField( read_only=False,view_name='to_org',queryset=Org.objects.all())
	# p2org_relation = serializers.HyperlinkedRelatedField( read_only=False,view_name='relationship_type',queryset=P2Org_Type.objects.all())
	class Meta:
		model = P2Org
		fields = ('id', 'from_ent', 'to_ent', 'relation', 'from_date', 'to_date', 'description')


class Org2PSerializer(serializers.HyperlinkedModelSerializer):
	# p_from_org = serializers.HyperlinkedRelatedField( read_only=False,view_name='from_org',queryset=Org.objects.all())
	# org_to_p = serializers.HyperlinkedRelatedField( read_only=False,view_name='to_person',queryset=Person.objects.all())
	# org2p_relation = serializers.HyperlinkedRelatedField( read_only=False,view_name='relationship_type',queryset=P2Org_Type.objects.all())
	class Meta:
		model = Org2P
		fields = ('id', 'from_ent', 'to_ent', 'relation', 'from_date', 'to_date', 'description')


class OrgHierarchySerializer(serializers.ModelSerializer):
	relation_type = serializers.SerializerMethodField()
	hierarchy = serializers.SerializerMethodField()
	member_count = serializers.SerializerMethodField()
	members = serializers.SerializerMethodField()
	children = serializers.SerializerMethodField()
	parents = serializers.SerializerMethodField()

	class Meta:
		model = Org
		fields = (
			'id',
			'slug',
			'orgName',
			'relation_type',
			'hierarchy',
			'member_count',
			'members',
			'children',
			'parents',
		)

	def _edge(self):
		return self.context.get('edge')

	def _employees(self, obj):
		cache = self.context.setdefault('_employees_cache', {})
		if obj.pk not in cache:
			cache[obj.pk] = list(obj.get_employees())
		return cache[obj.pk]

	def get_relation_type(self, obj):
		edge = self._edge()
		if edge and edge.relation:
			return edge.relation.relationship_type
		return None

	def get_hierarchy(self, obj):
		edge = self._edge()
		if edge:
			if edge.hierarchy == 'parent':
				return 'child'
			if edge.hierarchy == 'child':
				return 'parent'
			return edge.hierarchy
		return None

	def get_member_count(self, obj):
		return len(self._employees(obj))

	def get_members(self, obj):
		if not self.context.get('include_members'):
			return []
		members = []
		for person in self._employees(obj):
			members.append({
				'id': person.id,
				'slug': person.slug,
				'firstName': person.firstName,
				'lastName': person.lastName,
				'role': person.role.role if person.role else None,
			})
		return members

	def get_children(self, obj):
		direction = self.context.get('direction', 'down')
		if direction not in ('down', 'both'):
			return []
		depth = self.context.get('depth', 0)
		if depth <= 0:
			return []
		visited = self.context.get('visited') or set()
		children = []
		edges = obj.org_from_org.filter(hierarchy='parent').select_related('to_ent', 'relation').order_by('to_ent__orgName')
		for edge in edges:
			child = edge.to_ent
			if child.pk in visited:
				continue
			child_context = dict(self.context)
			child_context['depth'] = depth - 1
			child_context['edge'] = edge
			child_context['visited'] = set(visited) | {child.pk}
			serializer = OrgHierarchySerializer(child, context=child_context)
			children.append(serializer.data)
		return children

	def get_parents(self, obj):
		if not self.context.get('include_parents'):
			return []
		edges = obj.org_from_org.filter(hierarchy='child').select_related('to_ent', 'relation').order_by('to_ent__orgName')
		parents = []
		for edge in edges:
			parent = edge.to_ent
			parents.append({
				'id': parent.id,
				'slug': parent.slug,
				'orgName': parent.orgName,
				'hierarchy': 'parent',
				'relation_type': edge.relation.relationship_type if edge.relation else None,
			})
		return parents
