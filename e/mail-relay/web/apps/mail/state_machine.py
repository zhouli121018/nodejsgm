# coding=utf-8
from django_states.machine import StateMachine, StateDefinition, StateTransition


class MailStateMachine(StateMachine):
    log_transitions = False

    # possible states
    class check(StateDefinition):
        description = u'等待检测'
        initial = True

    class review(StateDefinition):
        description = u'等待审核'

    class reject(StateDefinition):
        description = u'拒绝'

    class dispatch(StateDefinition):
        description = u'等待分配IP'

    class send(StateDefinition):
        description = u'等待发送'

    class retry(StateDefinition):
        description = u'等待重试'

    class bounce(StateDefinition):
        description = u'等待退信'

    class finished(StateDefinition):
        description = u'完成'


    # state transitions
    class make_review(StateTransition):
        from_state = 'check'
        to_state = 'review'
        description = 'review'

    class make_dispatch(StateTransition):
        from_states = ('check', 'review')
        to_state = 'dispatch'
        description = 'dispatch'

    class make_reject(StateTransition):
        from_states = ('check', 'review')
        to_state = 'reject'
        description = 'reject'

    class make_send(StateTransition):
        from_state = 'dispatch'
        to_state = 'send'
        description = 'send'

    class make_retry(StateTransition):
        from_state = 'send'
        to_state = 'retry'
        description = 'send'

    class make_bounce(StateTransition):
        from_states = ('send', 'retry')
        to_state = 'bounce'
        description = 'bounce'

        def handler(transition, instance, user):
            instance.refresh_from_db()


    class make_finished(StateTransition):
        from_states = ('send', 'retry', 'bounce')
        to_state = 'finished'
        description = 'finished'
