def list_local_containers():
    try:
        import docker
        client = docker.from_env()
        return [{
            "id": c.short_id,
            "name": c.name,
            "image": c.image.tags[0] if c.image.tags else c.image.short_id,
            "status": c.status,
        } for c in client.containers.list(all=True)]
    except Exception:
        return []
