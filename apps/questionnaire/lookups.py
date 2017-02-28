from django.db.models import Lookup, Field


@Field.register_lookup
class QuestionnaireNameLookup(Lookup):
    """
    A simple lookup based on the assumption that the questionnaires name is
    stored in data -> qg_name -> []

    The use case is that superusers must search questionnaires by name, without
    regard to the status.

    Only the first element of 'qg_name'-list is searched in, and the whole
    content of this element is treated as text. So it is unprecise regarding
    target language and name / local_name, which is desirable in the current
    context.
    """
    lookup_name = 'qs_name'

    def as_postgresql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        # param must be escaped for '%<term>%'
        params = "%%%s%%" % connection.ops.prep_for_like_query(rhs_params[0])
        return "LOWER(%s -> 'qg_name' ->> 0) LIKE %s" % (lhs, rhs.lower()), [params]
