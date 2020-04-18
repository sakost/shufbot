from kutana import Plugin

plugin = Plugin('Configure[system]')


@plugin.on_start()
async def _(app):
    for backend in app.get_backends():
        if backend.get_identity() == 'vkontakte':
            app.config['owner_id'] = (await backend.resolve_screen_name(app.config['settings']['OWNER_ID']))['object_id']
            break

