export function slug(s: string): string {
<<<<<<< HEAD
  return s.toLowerCase().replace(/ /g, "-");
||||||| merged common ancestor
  return s.toLowerCase();
=======
  return s.trim().toLowerCase().replace(/\s+/g, "-");
>>>>>>> refactor/slug
}
