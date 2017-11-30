from utils import dd

class SearchParams(dd):
    def __init__(self, *argv, **kwargs):
        return dd.__init__(self,  *argv, **kwargs)
    def add_term(self, search_string, search_from=0, search_to=30, suggest_from=0, suggest_to=10):
        search_string = (u'|' + search_string)
        self['terms'][search_string] = {
            'titles': {
                'from': search_from,
                'to': search_to
            },
            'suggestions': {
                'from': suggest_from,
                'to': suggest_to
            }
        }
    def add_reference(self, ref_id, ref_from=0, ref_to=0, length=0):
        self['references'][ref_id] = {
            'from': ref_from,
            'to': ref_to,
            'length': length
        }
    def add_entity(self, type_id, ent_from=0, ent_to=30):
        self['entities'][type_id] = {
            'from': ent_from,
            'to': ent_to
        }
    def build_next_search(self, search_results):
        # (type) people not used
        next_search_params = SearchParams()
        for result,values in search_results.iteritems():
            ref_from = None
            ref_to = None
            length = values.get('length',0)
            type = values.get('type')
            type_id = values['type_id']
            subtype_id = values['subtype_id']
            search_param = (self[type][type_id][subtype_id] if subtype_id else self[type][type_id])
            if search_param:
                ref_from = (search_param['from'] + values.get('count',0) + 1)
                ref_to = (ref_from + (search_param['to'] - search_param['from']))
            if ref_from and ref_from < length:
                next_search_params.add_reference(
                    ref_id=result,
                    ref_from=ref_from,
                    ref_to=ref_to,
                    length=length
                )
        return next_search_params

class SearchResults(dd):
    def __init__(self, *argv, **kwargs):
        return dd.__init__(self,  *argv, **kwargs)
    @staticmethod
    def new_entity(type_id, type='', name=''):
        return {
            'type': type, #(person|genre|video)
            'type_id': type_id,
            'name': name
        }
    def add_result(self, ref_id, type=None, type_id=None, subtype_id=None, count=0, length=0, data=None):
        self[ref_id] = {
            'type': type, #(term|entity|reference)
            'type_id': type_id,
            'subtype_id': subtype_id,
            'count': count,
            'length': length,
            'data': data if data else {'videos': [], 'entities': []}
        }
    def has_results(self):
        count = 0
        length = 0
        for ref in self:
            count += self[ref].get('count',0)
            length += self[ref].get('length',0)
        if count or length:
            return True
        return False
