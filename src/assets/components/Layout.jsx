export function Layout({guide, content, side}) {
  return (
    <div class="layout">
      {guide && <section class="guide">{guide}</section>}
      {content && <section class="content">{content}</section>}
      {side && <section class="side">{side}</section>}
    </div>
  );
}
