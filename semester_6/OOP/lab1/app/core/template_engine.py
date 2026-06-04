from jinja2 import Environment, FileSystemLoader, select_autoescape


class TemplateEngine:
    def __init__(self, template_dir: str) -> None:
        self._env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(["html", "xml"]),
        )

    def render(self, template_name: str, model: dict) -> str:
        return self._env.get_template(template_name).render(**model)
