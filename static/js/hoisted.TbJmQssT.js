import "./hoisted.ZaE_CIdX.js";
function f() {
  const c = document.querySelector(".pricing-check"),
    l = document.querySelectorAll(".data-count");
  c &&
    c.addEventListener("change", function () {
      c.checked
        ? (l.forEach(function (t) {
            const e = t.getAttribute("data-count-yearly");
            e && ((t.innerHTML = e), r(t, parseInt(e, 10)));
          }),
          o(".text-yearly", "d-block", "hidden"),
          o(".text-monthly", "hidden", "d-block"))
        : (l.forEach(function (t) {
            const e = t.getAttribute("data-count-monthly");
            e && ((t.innerHTML = e), r(t, parseInt(e, 10)));
          }),
          o(".text-monthly", "d-block", "hidden"),
          o(".text-yearly", "hidden", "d-block"));
    });
  function r(t, e) {
    let i = 0;
    const a = 250;
    let n = null;
    function s(d) {
      n || (n = d);
      const u = d - n,
        h = Math.min(u / a, 1) * (e - i) + i;
      (t.innerHTML = Math.ceil(h).toString()),
        u < a && requestAnimationFrame(s);
    }
    requestAnimationFrame(s);
  }
  function o(t, e, i) {
    document.querySelectorAll(t).forEach(function (n) {
      n.classList.add(e), n.classList.remove(i);
    });
  }
}
document.addEventListener("astro:page-load", f);
