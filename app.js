// app.js
App({
  globalData: {
    userInfo: null,
    isLogin: false,
    dailyGoal: 30,
    dailyMinutes: 20,
    streak: 0,
    totalWords: 0,
    totalMinutes: 0,
    lastCheckinDate: '',
    todayWords: 0,
    todayMinutes: 0,
    points: 0,
    systemInfo: null
  },

  onLaunch(options) {
    // 获取系统信息
    this.globalData.systemInfo = wx.getSystemInfoSync();

    // 从本地存储恢复数据
    this.restoreData();

    // 初始化音频管理器（懒加载，仅注册引用）
    this.audioContext = null;

    // 检查每日打卡
    this.checkDailyCheckin();

    console.log('[App] 英语读背小程序启动', this.globalData.systemInfo.model);
  },

  onShow(options) {
    // 每次切到前台时检查打卡状态
    this.checkDailyCheckin();
  },

  onHide() {
    // 小程序进入后台时保存数据
    this.saveData();
  },

  /**
   * 每日打卡检查
   * 自动判断是否连续打卡，维护 streak 计数
   */
  checkDailyCheckin() {
    const today = this.getTodayStr();
    const lastDate = this.globalData.lastCheckinDate;

    if (!lastDate) {
      // 首次打开，记录今天
      this.globalData.lastCheckinDate = today;
      this.globalData.streak = 1;
      this.saveData();
      return;
    }

    if (lastDate === today) {
      // 今天已经打过卡，不做处理
      return;
    }

    // 检查是否为连续打卡（昨天打过卡）
    const yesterday = this.getDateStr(-1);
    if (lastDate === yesterday) {
      this.globalData.streak += 1;
    } else {
      // 中断，重新开始
      this.globalData.streak = 1;
    }

    // 重置今日数据
    this.globalData.todayWords = 0;
    this.globalData.todayMinutes = 0;
    this.globalData.lastCheckinDate = today;
    this.saveData();
  },

  /**
   * 增加背诵单词数
   */
  addWords(n) {
    this.globalData.todayWords += n;
    this.globalData.totalWords += n;
    this.addPoints(n * 1); // 每个单词1分
    this.saveData();
  },

  /**
   * 增加学习时长（分钟）
   */
  addMinutes(n) {
    this.globalData.todayMinutes += n;
    this.globalData.totalMinutes += n;
    this.saveData();
  },

  /**
   * 增加学习积分
   */
  addPoints(n) {
    this.globalData.points += n;
    this.saveData();
  },

  /**
   * 保存数据到本地存储
   */
  saveData() {
    const g = this.globalData;
    const data = {
      userInfo: g.userInfo,
      isLogin: g.isLogin,
      dailyGoal: g.dailyGoal,
      dailyMinutes: g.dailyMinutes,
      streak: g.streak,
      totalWords: g.totalWords,
      totalMinutes: g.totalMinutes,
      lastCheckinDate: g.lastCheckinDate,
      todayWords: g.todayWords,
      todayMinutes: g.todayMinutes,
      points: g.points
    };
    try {
      wx.setStorageSync('app_global_data', data);
    } catch (e) {
      console.error('[App] 保存数据失败', e);
    }
  },

  /**
   * 从本地存储恢复数据
   */
  restoreData() {
    try {
      const data = wx.getStorageSync('app_global_data');
      if (data) {
        const g = this.globalData;
        g.userInfo = data.userInfo || null;
        g.isLogin = data.isLogin || false;
        g.dailyGoal = data.dailyGoal || 30;
        g.dailyMinutes = data.dailyMinutes || 20;
        g.streak = data.streak || 0;
        g.totalWords = data.totalWords || 0;
        g.totalMinutes = data.totalMinutes || 0;
        g.lastCheckinDate = data.lastCheckinDate || '';
        g.todayWords = data.todayWords || 0;
        g.todayMinutes = data.todayMinutes || 0;
        g.points = data.points || 0;
      }
    } catch (e) {
      console.error('[App] 恢复数据失败', e);
    }
  },

  /**
   * 获取今天日期字符串 yyyy-MM-dd
   */
  getTodayStr() {
    const d = new Date();
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  },

  /**
   * 获取指定偏移的日期字符串
   * @param {number} offset 偏移天数，-1为昨天，1为明天
   */
  getDateStr(offset) {
    const d = new Date();
    d.setDate(d.getDate() + offset);
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  }
});
