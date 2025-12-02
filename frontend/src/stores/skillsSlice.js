import { skillsAPI } from '../services/api';

export const createSkillsSlice = (set, get) => ({
  skills: [],
  talents: [],
  tree: [],
  loadingSkills: false,

  setSkills: (skills) => set({ skills }),
  setTalents: (talents) => set({ talents }),
  setSkillsTree: (tree) => set({ tree }),

  fetchPlayerSkills: async () => {
    set({ loadingSkills: true });
    try {
      const { data } = await skillsAPI.getPlayerSkills();
      set({ skills: data.skills || [], talents: data.talents || [] });
    } catch (e) {
      // silent
    } finally {
      set({ loadingSkills: false });
    }
  },

  fetchSkillsTree: async () => {
    try {
      const { data } = await skillsAPI.getSkillsTree();
      set({ tree: data || [] });
    } catch (e) {
      // silent
    }
  },

  // Helpers
  getLevel: (skillCode) => {
    const s = get().skills.find((ps) => ps.skill?.code === skillCode);
    return s ? s.level : 1;
  },
  getXp: (skillCode) => {
    const s = get().skills.find((ps) => ps.skill?.code === skillCode);
    return s ? { xp: s.xp, xp_to_next: s.xp_to_next, total_xp: s.total_xp } : { xp: 0, xp_to_next: 50, total_xp: 0 };
  },
  hasTalent: (code) => get().talents.some((t) => t.talent_node?.code === code),
  getEffect: (effectType) => {
    const vals = get().talents
      .filter((t) => t.talent_node?.effect_type === effectType)
      .map((t) => t.talent_node?.effect_value || 0);
    return vals.length ? Math.max(...vals) : 0;
  },
});
