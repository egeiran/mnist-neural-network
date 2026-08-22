"use client";

import { useState } from "react";
import type { Copy, Lang } from "@/lib/copy";
import { SITE } from "@/lib/site";

/**
 * YouTube-embed som en «facade»: et stillbilde med play-knapp, og først når
 * noen trykker byttes det mot en ekte iframe.
 *
 * Grunnen er at en vanlig <iframe src="youtube.com/embed/…"> laster rundt en
 * megabyte JavaScript og setter sporingscookies på HVER sidevisning, også for
 * alle som aldri ser filmen. Slik betaler bare de som faktisk vil se.
 * nocookie-domenet gjør resten.
 */
export default function Film({ copy, lang }: { copy: Copy; lang: Lang }) {
  const [playingFrom, setPlayingFrom] = useState<number | null>(null);
  const id = SITE.youtubeId;

  function play(at: number) {
    setPlayingFrom(at);
  }

  return (
    <>
      <div className="player">
        {!id ? (
          <p className="missing">{copy.video.missing}</p>
        ) : playingFrom !== null ? (
          <iframe
            src={`https://www.youtube-nocookie.com/embed/${id}?autoplay=1&start=${playingFrom}&rel=0`}
            title={copy.video.title}
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; picture-in-picture"
            allowFullScreen
          />
        ) : (
          <button type="button" className="playBtn" onClick={() => play(0)}>
            <span className="playCircle" aria-hidden="true">
              <svg width="26" height="26" viewBox="0 0 24 24" fill="currentColor">
                <path d="M8 5v14l11-7z" />
              </svg>
            </span>
            <span className="playLabel">{copy.video.play}</span>
          </button>
        )}
      </div>

      {id ? (
        <>
          <p className="subhead">{copy.video.chapters}</p>
          <div className="chapters">
            {SITE.chapters.map((chapter) => (
              <button
                type="button"
                key={chapter.at}
                className="chapter"
                onClick={() => play(chapter.at)}
              >
                <time>
                  {Math.floor(chapter.at / 60)}:
                  {String(chapter.at % 60).padStart(2, "0")}
                </time>
                {chapter[lang]}
              </button>
            ))}
          </div>
        </>
      ) : null}
    </>
  );
}
