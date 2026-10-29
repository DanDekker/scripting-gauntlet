// dashboard bootstrap - t("app.title") is used below
const title = t("app.title");
const decoy = 't("not.a.call")';
// t("commented.key") was retired in 0.3
const greeting = t('app.welcome');
const close = i18n.t("button.close");

export function render() {
  return t(
    "app.fresh"
  );
}
