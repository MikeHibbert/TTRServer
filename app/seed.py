from __future__ import annotations

from sqlalchemy.orm import Session
from .database import SessionLocal, Base, engine
from .models import Vignette, Asset3D
from .services.embeddings import embed_text


VIGNETTES = [
    {"house_num": 1, "base_prompt": "family hiding under table during bombing", "memory_script": "Hold your breath—shadows pass."},
    {"house_num": 2, "base_prompt": "cracked locket on rubble floor, war-torn bedroom", "memory_script": "The song inside is broken."},
    {"house_num": 3, "base_prompt": "shadowy figures in doorway, fear pressing in", "memory_script": "Bad men at door—hide!"},
    {"house_num": 4, "base_prompt": "ethereal mother hugging child in golden light, ruins", "memory_script": "Her arms are warm, even in ash."},
    {"house_num": 5, "base_prompt": "judicial scales motif among ocean debris for Scales", "memory_script": "Weigh what's left of home."},
]


ASSETS = [
    {"prompt": "cracked music box with faded gold, on dusty floor", "gltf_url": "https://example.com/assets/music_box.glb"},
    {"prompt": "shadowy doorway frame with splintered wood and iron latch", "gltf_url": "https://example.com/assets/doorway.glb"},
    {"prompt": "judicial scales half-buried in sand, seaweed textures", "gltf_url": "https://example.com/assets/scales_sea.glb"},
]


def main():
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    try:
        # Seed vignettes
        for v in VIGNETTES:
            exists = db.query(Vignette).filter(Vignette.house_num == v["house_num"]).first()
            if not exists:
                db.add(Vignette(**v))

        # Seed 3D assets with embeddings in metadata
        for a in ASSETS:
            exists = db.query(Asset3D).filter(Asset3D.gltf_url == a["gltf_url"]).first()
            if not exists:
                emb = embed_text(a["prompt"])  # precompute embedding
                db.add(Asset3D(prompt=a["prompt"], gltf_url=a["gltf_url"], meta={"embedding": emb}))

        db.commit()
        print("Seed completed: vignettes and 3D assets.")
    finally:
        db.close()


if __name__ == "__main__":
    main()