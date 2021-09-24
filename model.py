from dataclasses import dataclass


@dataclass
class MScore:
    module: str
    year: str
    period: str
    date_score: str
    date_publish: str

@dataclass
class MScoreDist:
    results: list[int]
    texts: list[str]
    open: int
    done: int

    @property
    def total(self):
        return self.open + self.done

    def get_mark_text(self, mark):
        return f"{mark + 1} ({self.texts[mark]})"

    def get_embed_dict(self, mark):
        return {
            "name": self.get_mark_text(mark),
            "value": str(self.results[mark])
        }