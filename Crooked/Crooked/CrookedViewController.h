//
//  CrookedViewController.h
//  Crooked
//
//  Created by Aaron Stacy on 11/25/11.
//  Copyright (c) 2011 StoredIQ. All rights reserved.
//

#import <UIKit/UIKit.h>
#import <AVFoundation/AVFoundation.h>

@interface CrookedViewController : UIViewController <AVAudioPlayerDelegate> {
    AVAudioPlayer* player;
    AVAudioRecorder* recorder;
}

@property (weak, nonatomic) IBOutlet UIButton* recordButton;

@property (weak, nonatomic) IBOutlet UIButton* playButton;

@property (copy, nonatomic) NSURL* url;

@property (strong, nonatomic) NSMutableDictionary* recordSettings;

- (IBAction)record:(id)sender;

- (void)startRecord;

- (void)stopRecord;

- (IBAction)play:(id)sender;

- (void)startPlay;

- (void)stopPlay;
- (void)audioPlayerDidFinishPlaying:(AVAudioPlayer*)plyr successfully:(BOOL)flag;

@end
